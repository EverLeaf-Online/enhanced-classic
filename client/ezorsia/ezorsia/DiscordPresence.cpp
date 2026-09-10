#include "stdafx.h"
#ifndef EVERLEAF_PRESENCE_TEST
#include "DiscordPresence.h"
#include "INIReader.h"
#include "CrashDiagnostics.h"
#include "Memory.h"
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
constexpr DWORD kGameplayRefreshMs = 1000;
constexpr ULONGLONG kFileTimeUnixEpoch = 116444736000000000ULL;

// GMS v83.1 contracts pinned from Angel.idb and independently corroborated by
// the EverLeaf/Kaentake/Chronicle client work. Do not port these addresses to a
// different client build without re-verifying that build's memory contracts.
constexpr DWORD kWvsContextInstanceAddress = 0x00BE7918;
constexpr DWORD kUserLocalInstanceAddress = 0x00BEBF98;
constexpr DWORD kGetFieldAddress = 0x00437A0C;
constexpr DWORD kGetCharacterNameAddress = 0x004AC308;
constexpr DWORD kUserLocalUpdateAddress = 0x0094A144;
constexpr DWORD kGetCharacterLevelAddress = 0x00949B15;
constexpr DWORD kGetJobCodeAddress = 0x0095FFC3;
constexpr DWORD kGetFieldIdAddress = 0x009613E0;
constexpr DWORD kGetCurFieldIdAddress = 0x00A1238B;

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

const char* JobName(int job) {
    switch (job) {
    case 0: return "Beginner";
    case 100: return "Warrior";
    case 110: return "Fighter";
    case 111: return "Crusader";
    case 112: return "Hero";
    case 120: return "Page";
    case 121: return "White Knight";
    case 122: return "Paladin";
    case 130: return "Spearman";
    case 131: return "Dragon Knight";
    case 132: return "Dark Knight";
    case 200: return "Magician";
    case 210: return "F/P Wizard";
    case 211: return "F/P Mage";
    case 212: return "F/P Arch Mage";
    case 220: return "I/L Wizard";
    case 221: return "I/L Mage";
    case 222: return "I/L Arch Mage";
    case 230: return "Cleric";
    case 231: return "Priest";
    case 232: return "Bishop";
    case 300: return "Bowman";
    case 310: return "Hunter";
    case 311: return "Ranger";
    case 312: return "Bowmaster";
    case 320: return "Crossbowman";
    case 321: return "Sniper";
    case 322: return "Marksman";
    case 400: return "Thief";
    case 410: return "Assassin";
    case 411: return "Hermit";
    case 412: return "Night Lord";
    case 420: return "Bandit";
    case 421: return "Chief Bandit";
    case 422: return "Shadower";
    case 500: return "Pirate";
    case 510: return "Brawler";
    case 511: return "Marauder";
    case 512: return "Buccaneer";
    case 520: return "Gunslinger";
    case 521: return "Outlaw";
    case 522: return "Corsair";
    case 800: return "MapleLeaf Brigadier";
    case 900: return "GM";
    case 910: return "SuperGM";
    case 1000: return "Noblesse";
    case 1100: case 1110: case 1111: case 1112: return "Dawn Warrior";
    case 1200: case 1210: case 1211: case 1212: return "Blaze Wizard";
    case 1300: case 1310: case 1311: case 1312: return "Wind Archer";
    case 1400: case 1410: case 1411: case 1412: return "Night Walker";
    case 1500: case 1510: case 1511: case 1512: return "Thunder Breaker";
    case 2000: return "Legend";
    case 2001: return "Evan";
    case 2100: case 2110: case 2111: case 2112: return "Aran";
    case 2200: case 2210: case 2211: case 2212: case 2213:
    case 2214: case 2215: case 2216: case 2217: case 2218: return "Evan";
    default: return "Unknown Job";
    }
}

std::string BuildGameplayDetails(const std::string& name, unsigned int level, int job) {
    std::ostringstream text;
    text << name << " | Lv. " << level << " " << JobName(job);
    return text.str();
}

std::string BuildGameplayState(unsigned long fieldId) {
    return std::string("Map ") + std::to_string(fieldId);
}

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
        if (pipe != INVALID_HANDLE_VALUE) return pipe;
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

#ifndef EVERLEAF_PRESENCE_TEST
struct GameplaySnapshot {
    char name[32];
    unsigned int level;
    int job;
    unsigned long fieldId;
};

using CUserLocalUpdate_t = void(__thiscall*)(void*);
using GetCharacterName_t = const char* (__thiscall*)(void*);
using GetCharacterLevel_t = unsigned char (__thiscall*)(void*);
using GetJobCode_t = int (__thiscall*)(void*);
using GetFieldId_t = unsigned long (__thiscall*)(void*);
using GetCurFieldId_t = int (__thiscall*)(void*);
using GetField_t = void* (__cdecl*)();

CUserLocalUpdate_t gUserLocalUpdateOriginal =
    reinterpret_cast<CUserLocalUpdate_t>(kUserLocalUpdateAddress);
GetCharacterName_t gGetCharacterName =
    reinterpret_cast<GetCharacterName_t>(kGetCharacterNameAddress);
GetCharacterLevel_t gGetCharacterLevel =
    reinterpret_cast<GetCharacterLevel_t>(kGetCharacterLevelAddress);
GetJobCode_t gGetJobCode = reinterpret_cast<GetJobCode_t>(kGetJobCodeAddress);
GetFieldId_t gGetFieldId = reinterpret_cast<GetFieldId_t>(kGetFieldIdAddress);
GetCurFieldId_t gGetCurFieldId = reinterpret_cast<GetCurFieldId_t>(kGetCurFieldIdAddress);
GetField_t gGetField = reinterpret_cast<GetField_t>(kGetFieldAddress);

bool gGameplayHookInstalled = false;
bool gGameplayActivityVisible = false;
ULONGLONG gLastGameplayRefresh = 0;

bool TryReadGameplaySnapshot(void* localUser, GameplaySnapshot* snapshot) {
    if (!localUser || !snapshot) return false;

    __try {
        void* singletonUser = *reinterpret_cast<void**>(kUserLocalInstanceAddress);
        void* context = *reinterpret_cast<void**>(kWvsContextInstanceAddress);
        if (!singletonUser || singletonUser != localUser || !context || !gGetField()) {
            return false;
        }

        const char* name = gGetCharacterName(context);
        if (!name) return false;

        size_t length = 0;
        while (length < sizeof(snapshot->name) - 1 && name[length] != '\0') {
            const unsigned char c = static_cast<unsigned char>(name[length]);
            if (c < 0x20 || c == 0x7f) return false;
            snapshot->name[length] = name[length];
            ++length;
        }
        if (length == 0 || name[length] != '\0') return false;
        snapshot->name[length] = '\0';

        const unsigned int level = gGetCharacterLevel(localUser);
        const int job = gGetJobCode(localUser);
        const unsigned long localFieldId = gGetFieldId(localUser);
        const int contextFieldId = gGetCurFieldId(context);
        if (level == 0 || contextFieldId < 0
            || localFieldId != static_cast<unsigned long>(contextFieldId)) {
            return false;
        }

        snapshot->level = level;
        snapshot->job = job;
        snapshot->fieldId = localFieldId;
        return true;
    }
    __except (EXCEPTION_EXECUTE_HANDLER) {
        return false;
    }
}

void SetBasicActivity() {
    if (!gGameplayActivityVisible) return;
    SetActivity("Exploring EverLeaf", "Enhanced classic adventure");
    gGameplayActivityVisible = false;
}

void RefreshGameplayActivity(void* localUser) {
    const ULONGLONG now = GetTickCount64();
    if (gLastGameplayRefresh != 0 && now - gLastGameplayRefresh < kGameplayRefreshMs) {
        return;
    }
    gLastGameplayRefresh = now;

    GameplaySnapshot snapshot{};
    if (!TryReadGameplaySnapshot(localUser, &snapshot)) {
        SetBasicActivity();
        return;
    }

    SetActivity(
        BuildGameplayDetails(snapshot.name, snapshot.level, snapshot.job),
        BuildGameplayState(snapshot.fieldId));
    gGameplayActivityVisible = true;
}

void __fastcall CUserLocalUpdateHook(void* pThis, void*) {
    gUserLocalUpdateOriginal(pThis);
    RefreshGameplayActivity(pThis);
}

bool InstallGameplayHook() {
    if (gGameplayHookInstalled) return true;
    if (!gUserLocalUpdateOriginal) return false;

    if (!Memory::SetHook(
            true,
            reinterpret_cast<void**>(&gUserLocalUpdateOriginal),
            reinterpret_cast<void*>(CUserLocalUpdateHook))) {
        return false;
    }

    gGameplayHookInstalled = true;
    return true;
}
#endif

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
    if (gRunning.exchange(true)) return;

    INIReader config("config.ini");
    if (!config.GetBoolean("general", "DiscordRichPresence", true)) {
        gRunning.store(false);
        return;
    }

#ifndef EVERLEAF_PRESENCE_TEST
    if (!InstallGameplayHook()) {
        CrashDiagnostics::LogEvent("Discord Rich Presence gameplay hook unavailable; using basic activity");
    } else {
        CrashDiagnostics::LogEvent("Discord Rich Presence v83 gameplay hook installed");
    }
#endif

    gStopRequested.store(false);
    FILETIME now;
    GetSystemTimeAsFileTime(&now);
    ULARGE_INTEGER nowValue{};
    nowValue.LowPart = now.dwLowDateTime;
    nowValue.HighPart = now.dwHighDateTime;
    gStartedAtSeconds = (nowValue.QuadPart - kFileTimeUnixEpoch) / 10000000ULL;

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
    gStopRequested.store(true);
}

void SetActivity(const std::string& details, const std::string& state) {
    std::lock_guard<std::mutex> lock(gActivityMutex);
    gDetails = details.empty() ? "Exploring EverLeaf" : details;
    gState = state.empty() ? "Enhanced classic adventure" : state;
}
} // namespace DiscordPresence
