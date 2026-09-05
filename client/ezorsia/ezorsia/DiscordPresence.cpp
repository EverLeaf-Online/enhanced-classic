#include "stdafx.h"
#include "DiscordPresence.h"
#include "INIReader.h"
#include "CrashDiagnostics.h"

#include <atomic>
#include <cstdint>
#include <mutex>
#include <sstream>
#include <string>

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

bool WriteAll(HANDLE pipe, const void* bytes, DWORD length) {
    const BYTE* cursor = static_cast<const BYTE*>(bytes);
    DWORD remaining = length;
    while (remaining > 0) {
        DWORD written = 0;
        if (!WriteFile(pipe, cursor, remaining, &written, nullptr) || written == 0) {
            return false;
        }
        cursor += written;
        remaining -= written;
    }
    return true;
}

bool SendFrame(HANDLE pipe, Opcode opcode, const std::string& payload) {
    if (payload.size() > UINT32_MAX) {
        return false;
    }
    const FrameHeader header{
        static_cast<std::uint32_t>(opcode),
        static_cast<std::uint32_t>(payload.size())
    };
    return WriteAll(pipe, &header, sizeof(header))
        && WriteAll(pipe, payload.data(), header.length);
}

void DrainPipe(HANDLE pipe) {
    BYTE buffer[4096];
    for (;;) {
        DWORD available = 0;
        if (!PeekNamedPipe(pipe, nullptr, 0, nullptr, &available, nullptr) || available == 0) {
            return;
        }
        DWORD read = 0;
        const DWORD requested = available < sizeof(buffer) ? available : sizeof(buffer);
        if (!ReadFile(pipe, buffer, requested, &read, nullptr) || read == 0) {
            return;
        }
    }
}

HANDLE ConnectPipe() {
    for (int index = 0; index < 10; ++index) {
        const std::wstring name = L"\\\\.\\pipe\\discord-ipc-" + std::to_wstring(index);
        HANDLE pipe = CreateFileW(
            name.c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr,
            OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
        if (pipe != INVALID_HANDLE_VALUE) {
            return pipe;
        }
    }
    return INVALID_HANDLE_VALUE;
}

std::string BuildHandshake() {
    return std::string("{\"v\":1,\"client_id\":\"") + kApplicationId + "\"}";
}

std::string BuildActivity() {
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
        << "]}}},\"nonce\":\"" << GetTickCount64() << "\"}";
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

DWORD WINAPI WorkerProc(LPVOID) {
    while (!gStopRequested.load()) {
        HANDLE pipe = ConnectPipe();
        if (pipe == INVALID_HANDLE_VALUE) {
            SleepUntil(kReconnectDelayMs);
            continue;
        }

        if (!SendFrame(pipe, Opcode::Handshake, BuildHandshake())
            || !SleepUntil(250)) {
            CloseHandle(pipe);
            SleepUntil(kReconnectDelayMs);
            continue;
        }
        DrainPipe(pipe);
        if (!SendFrame(pipe, Opcode::Frame, BuildActivity())) {
            CloseHandle(pipe);
            SleepUntil(kReconnectDelayMs);
            continue;
        }

        CrashDiagnostics::LogEvent("Discord Rich Presence connected");
        while (SleepUntil(kRefreshDelayMs)) {
            DrainPipe(pipe);
            if (!SendFrame(pipe, Opcode::Frame, BuildActivity())) {
                break;
            }
        }
        CloseHandle(pipe);
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
