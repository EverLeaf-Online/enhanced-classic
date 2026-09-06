#include "stdafx.h"
#ifndef EVERLEAF_PRESENCE_TEST
#include "DiscordPresence.h"
#include "INIReader.h"
#include "CrashDiagnostics.h"
#endif

#include <atomic>
#include <cstdint>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>
#include <cstring>
#include <cctype>

namespace DiscordPresence {
namespace {
constexpr const char* kApplicationId = "1542634637862633602";
constexpr DWORD kReconnectDelayMs = 15000;
constexpr DWORD kRefreshDelayMs = 30000;
constexpr DWORD kSleepSliceMs = 250;
constexpr ULONGLONG kFileTimeUnixEpoch = 116444736000000000ULL;

enum class Opcode : std::uint32_t {
    Handshake = 0,
    Frame = 1,
    Close = 2,
    Ping = 3,
    Pong = 4,
};

#pragma pack(push, 1)
struct FrameHeader {
    std::uint32_t opcode;
    std::uint32_t length;
};
#pragma pack(pop)

std::atomic<bool> gRunning{ false };
std::atomic<bool> gStopRequested{ false };
std::mutex gActivityMutex;
std::string gDetails = "Exploring EverLeaf";
std::string gState = "Enhanced classic adventure";
ULONGLONG gStartedAtSeconds = 0;

std::string EscapeJson(const std::string& value) {
    std::ostringstream output;
    static const char* hex = "0123456789abcdef";
    for (const unsigned char character : value) {
        switch (character) {
        case '"': output << "\\\""; break;
        case '\\': output << "\\\\"; break;
        case '\b': output << "\\b"; break;
        case '\f': output << "\\f"; break;
        case '\n': output << "\\n"; break;
        case '\r': output << "\\r"; break;
        case '\t': output << "\\t"; break;
        default:
            if (character < 0x20) {
                output << "\\u00" << hex[character >> 4] << hex[character & 0x0f];
            } else {
                output << static_cast<char>(character);
            }
        }
    }
    return output.str();
}

// All IPC is bounded and confined to this optional worker.
bool Transfer(HANDLE pipe, void* bytes, DWORD length, bool write) {
    OVERLAPPED operation{};
    operation.hEvent = CreateEventW(nullptr, TRUE, FALSE, nullptr);
    if (!operation.hEvent) return false;
    DWORD transferred = 0;
    BOOL ok = write ? WriteFile(pipe, bytes, length, &transferred, &operation)
                    : ReadFile(pipe, bytes, length, &transferred, &operation);
    if (!ok && GetLastError() == ERROR_IO_PENDING) {
        if (WaitForSingleObject(operation.hEvent, 1500) != WAIT_OBJECT_0) {
            CancelIoEx(pipe, &operation);
            GetOverlappedResult(pipe, &operation, &transferred, TRUE);
            CloseHandle(operation.hEvent);
            return false;
        }
        ok = GetOverlappedResult(pipe, &operation, &transferred, FALSE);
    }
    CloseHandle(operation.hEvent);
    return ok && transferred == length;
}

bool SendFrame(HANDLE pipe, Opcode opcode, const std::string& payload) {
    if (payload.size() > 65536) return false;
    const FrameHeader header{static_cast<std::uint32_t>(opcode),
        static_cast<std::uint32_t>(payload.size())};
    std::vector<BYTE> bytes(sizeof(header) + payload.size());
    std::memcpy(bytes.data(), &header, sizeof(header));
    std::memcpy(bytes.data() + sizeof(header), payload.data(), payload.size());
    // Discord expects the header and JSON in one write.
    return Transfer(pipe, bytes.data(), static_cast<DWORD>(bytes.size()), true);
}

bool StringFieldEquals(const std::string& json, const std::string& key,
                       const std::string& expected) {
    const auto found = json.find("\"" + key + "\"");
    if (found == std::string::npos) return false;
    auto at = found + key.size() + 2;
    while (at < json.size() && std::isspace(static_cast<unsigned char>(json[at]))) ++at;
    if (at == json.size() || json[at++] != ':') return false;
    while (at < json.size() && std::isspace(static_cast<unsigned char>(json[at]))) ++at;
    return json.compare(at, expected.size() + 2, "\"" + expected + "\"") == 0;
}

struct Incoming {
    std::vector<BYTE> bytes;
    bool ready = false;
    bool acknowledged = false;
};

bool ProcessIncoming(HANDLE pipe, Incoming& incoming, const std::string& nonce) {
    while (incoming.bytes.size() >= sizeof(FrameHeader)) {
        FrameHeader header{};
        std::memcpy(&header, incoming.bytes.data(), sizeof(header));
        if (header.length > 65536) return false;
        const size_t size = sizeof(header) + header.length;
        if (incoming.bytes.size() < size) break;
        std::string payload(reinterpret_cast<const char*>(incoming.bytes.data() + sizeof(header)), header.length);
        incoming.bytes.erase(incoming.bytes.begin(), incoming.bytes.begin() + size);
        const auto opcode = static_cast<Opcode>(header.opcode);
        if (opcode == Opcode::Close) return false;
        if (opcode == Opcode::Ping) {
            if (!SendFrame(pipe, Opcode::Pong, payload)) return false;
        } else if (opcode == Opcode::Frame) {
            if (StringFieldEquals(payload, "evt", "ERROR")) {
                CrashDiagnostics::LogEvent("Discord Rich Presence request rejected");
                return false;
            }
            if (StringFieldEquals(payload, "evt", "READY")) incoming.ready = true;
            if (!nonce.empty() && StringFieldEquals(payload, "cmd", "SET_ACTIVITY")
                && StringFieldEquals(payload, "nonce", nonce)) incoming.acknowledged = true;
        } else if (opcode != Opcode::Pong) return false;
    }
    return true;
}

bool PollPipe(HANDLE pipe, Incoming& incoming, const std::string& nonce) {
    DWORD available = 0;
    if (!PeekNamedPipe(pipe, nullptr, 0, nullptr, &available, nullptr)) return false;
    if (available) {
        BYTE buffer[4096];
        const DWORD count = available < sizeof(buffer) ? available : sizeof(buffer);
        if (!Transfer(pipe, buffer, count, false)) return false;
        incoming.bytes.insert(incoming.bytes.end(), buffer, buffer + count);
    }
    return ProcessIncoming(pipe, incoming, nonce);
}

HANDLE ConnectPipe() {
    for (int index = 0; index < 10; ++index) {
        const std::wstring name = L"\\\\.\\pipe\\discord-ipc-" + std::to_wstring(index);
        HANDLE pipe = CreateFileW(
            name.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr,
            OPEN_EXISTING, FILE_FLAG_OVERLAPPED, nullptr);
        if (pipe != INVALID_HANDLE_VALUE) {
            return pipe;
        }
    }
    return INVALID_HANDLE_VALUE;
}

std::string BuildHandshake() {
    return std::string("{\"v\":1,\"client_id\":\"") + kApplicationId + "\"}";
}

std::string BuildActivity(const std::string& nonce) {
    std::string details;
    std::string state;
    {
        std::lock_guard<std::mutex> lock(gActivityMutex);
        details = gDetails;
        state = gState;
    }

    std::ostringstream payload;
    payload
        << "{\"cmd\":\"SET_ACTIVITY\",\"args\":{\"pid\":" << GetCurrentProcessId()
        << ",\"activity\":{\"details\":\"" << EscapeJson(details)
        << "\",\"state\":\"" << EscapeJson(state)
        << "\",\"timestamps\":{\"start\":" << gStartedAtSeconds
        << "},\"buttons\":["
        << "{\"label\":\"Visit EverLeaf\",\"url\":\"https://everleafms.online\"},"
        << "{\"label\":\"Join Discord\",\"url\":\"https://discord.gg/w9ED8vtxa7\"}"
        << "]}},\"nonce\":\"" << EscapeJson(nonce) << "\"}";
    return payload.str();
}

bool SleepUntil(DWORD durationMs) {
    DWORD elapsed = 0;
    while (elapsed < durationMs && !gStopRequested.load()) {
        const DWORD remaining = durationMs - elapsed;
        const DWORD slice = remaining < kSleepSliceMs ? remaining : kSleepSliceMs;
        Sleep(slice);
        elapsed += slice;
    }
    return !gStopRequested.load();
}

bool WaitForResponse(HANDLE pipe, Incoming& incoming, const std::string& nonce) {
    const ULONGLONG deadline = GetTickCount64() + 5000;
    while (!gStopRequested.load() && GetTickCount64() < deadline) {
        if (!PollPipe(pipe, incoming, nonce)) return false;
        if (nonce.empty() ? incoming.ready : incoming.acknowledged) return true;
        if (!SleepUntil(25)) break;
    }
    return false;
}

DWORD WINAPI WorkerProc(LPVOID) {
    while (!gStopRequested.load()) {
        HANDLE pipe = ConnectPipe();
        if (pipe == INVALID_HANDLE_VALUE) {
            SleepUntil(kReconnectDelayMs);
            continue;
        }
        Incoming incoming;
        if (!SendFrame(pipe, Opcode::Handshake, BuildHandshake())
            || !WaitForResponse(pipe, incoming, "")) {
            CloseHandle(pipe);
            SleepUntil(kReconnectDelayMs);
            continue;
        }
        bool announced = false;
        while (!gStopRequested.load()) {
            const std::string nonce = std::to_string(GetTickCount64());
            incoming.acknowledged = false;
            if (!SendFrame(pipe, Opcode::Frame, BuildActivity(nonce))
                || !WaitForResponse(pipe, incoming, nonce)) break;
            if (!announced) {
                CrashDiagnostics::LogEvent("Discord Rich Presence activity acknowledged");
                announced = true;
            }
            const ULONGLONG refreshAt = GetTickCount64() + kRefreshDelayMs;
            bool healthy = true;
            while (GetTickCount64() < refreshAt && !gStopRequested.load()) {
                if (!PollPipe(pipe, incoming, nonce)) { healthy = false; break; }
                SleepUntil(kSleepSliceMs);
            }
            if (!healthy) break;
        }
        CloseHandle(pipe);
        SleepUntil(kReconnectDelayMs);
    }
    gRunning.store(false);
    return 0;
}
} // namespace

void Start() {
    if (gRunning.exchange(true)) {
        return;
    }

    INIReader config("config.ini");
    if (!config.GetBoolean("general", "DiscordRichPresence", true)) {
        gRunning.store(false);
        return;
    }

    gStopRequested.store(false);
    FILETIME now;
    GetSystemTimeAsFileTime(&now);
    ULARGE_INTEGER nowValue{};
    nowValue.LowPart = now.dwLowDateTime;
    nowValue.HighPart = now.dwHighDateTime;
    gStartedAtSeconds = (nowValue.QuadPart - kFileTimeUnixEpoch) / 10000000ULL;

    // The worker must never execute from an unloaded DLL. Pin for game lifetime.
    HMODULE module = nullptr;
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_PIN,
        reinterpret_cast<LPCWSTR>(&WorkerProc), &module)) {
        gRunning.store(false);
        return;
    }
    HANDLE worker = CreateThread(nullptr, 0, WorkerProc, nullptr, 0, nullptr);
    if (!worker) {
        gRunning.store(false);
        CrashDiagnostics::LogEvent("Discord Rich Presence worker unavailable");
        return;
    }
    CloseHandle(worker);
}

void Stop() {
    // DllMain can run under the loader lock, so shutdown must never wait here.
    gStopRequested.store(true);
}

void SetActivity(const std::string& details, const std::string& state) {
    std::lock_guard<std::mutex> lock(gActivityMutex);
    gDetails = details.empty() ? "Exploring EverLeaf" : details;
    gState = state.empty() ? "Enhanced classic adventure" : state;
}
} // namespace DiscordPresence
