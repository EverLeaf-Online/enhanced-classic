#include "pch.h"
#include "hook.h"

#include <shellapi.h>
#include <algorithm>
#include <cctype>
#include <string>

namespace {
constexpr const char* kEverLeafHome = "https://everleafms.online/";
constexpr const char* kEverLeafRegister = "https://everleafms.online/register";
constexpr const char* kEverLeafHelp = "https://everleafms.online/help";

using ShellExecuteA_t = HINSTANCE (WINAPI*)(HWND, LPCSTR, LPCSTR, LPCSTR, LPCSTR, INT);
using ShellExecuteW_t = HINSTANCE (WINAPI*)(HWND, LPCWSTR, LPCWSTR, LPCWSTR, LPCWSTR, INT);

ShellExecuteA_t g_ShellExecuteA = reinterpret_cast<ShellExecuteA_t>(GetAddress("SHELL32", "ShellExecuteA"));
ShellExecuteW_t g_ShellExecuteW = reinterpret_cast<ShellExecuteW_t>(GetAddress("SHELL32", "ShellExecuteW"));

std::string LowerAscii(std::string value) {
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });
    return value;
}

bool StartsWith(const std::string& value, const char* prefix) {
    const size_t n = strlen(prefix);
    return value.size() >= n && value.compare(0, n, prefix) == 0;
}

bool IsLegacyNexonUrl(const std::string& input) {
    const std::string lower = LowerAscii(input);
    if (!StartsWith(lower, "http://") && !StartsWith(lower, "https://")) return false;
    const auto scheme = lower.find("://");
    if (scheme == std::string::npos) return false;
    const size_t hostStart = scheme + 3;
    size_t hostEnd = lower.find_first_of("/:?#", hostStart);
    if (hostEnd == std::string::npos) hostEnd = lower.size();
    const std::string host = lower.substr(hostStart, hostEnd - hostStart);
    return host == "nexon.net" || host == "www.nexon.net" ||
           host == "maplestory.nexon.net" || host == "maplestory.nexon.com" ||
           (host.size() > 10 && host.compare(host.size() - 10, 10, ".nexon.net") == 0) ||
           (host.size() > 10 && host.compare(host.size() - 10, 10, ".nexon.com") == 0);
}

const char* RouteLegacyUrl(const char* file) {
    if (!file || !*file) return file;
    const std::string original(file);
    if (!IsLegacyNexonUrl(original)) return file;
    const std::string lower = LowerAscii(original);
    if (lower.find("register") != std::string::npos ||
        lower.find("signup") != std::string::npos ||
        lower.find("sign-up") != std::string::npos ||
        lower.find("join") != std::string::npos) {
        return kEverLeafRegister;
    }
    if (lower.find("password") != std::string::npos ||
        lower.find("passwd") != std::string::npos ||
        lower.find("forgot") != std::string::npos ||
        lower.find("findid") != std::string::npos ||
        lower.find("find_id") != std::string::npos ||
        lower.find("find-id") != std::string::npos ||
        lower.find("account") != std::string::npos ||
        lower.find("member") != std::string::npos) {
        return kEverLeafHelp;
    }
    return kEverLeafHome;
}

std::wstring RouteLegacyUrl(const wchar_t* file) {
    if (!file || !*file) return {};
    const int bytes = WideCharToMultiByte(CP_UTF8, 0, file, -1, nullptr, 0, nullptr, nullptr);
    if (bytes <= 1) return file;
    std::string utf8(static_cast<size_t>(bytes - 1), '\0');
    WideCharToMultiByte(CP_UTF8, 0, file, -1, utf8.data(), bytes, nullptr, nullptr);
    const char* routed = RouteLegacyUrl(utf8.c_str());
    if (routed == utf8.c_str() || strcmp(routed, utf8.c_str()) == 0) return file;
    const int wideCount = MultiByteToWideChar(CP_UTF8, 0, routed, -1, nullptr, 0);
    if (wideCount <= 1) return file;
    std::wstring wide(static_cast<size_t>(wideCount - 1), L'\0');
    MultiByteToWideChar(CP_UTF8, 0, routed, -1, wide.data(), wideCount);
    return wide;
}

HINSTANCE WINAPI ShellExecuteA_hook(HWND hwnd, LPCSTR operation, LPCSTR file,
                                    LPCSTR parameters, LPCSTR directory, INT showCmd) {
    const char* routed = RouteLegacyUrl(file);
    if (routed != file) DEBUG_MESSAGE("Redirecting legacy Nexon URL to EverLeaf");
    return g_ShellExecuteA(hwnd, operation, routed, parameters, directory, showCmd);
}

HINSTANCE WINAPI ShellExecuteW_hook(HWND hwnd, LPCWSTR operation, LPCWSTR file,
                                    LPCWSTR parameters, LPCWSTR directory, INT showCmd) {
    std::wstring routed = RouteLegacyUrl(file);
    const wchar_t* target = routed.empty() ? file : routed.c_str();
    if (target != file) DEBUG_MESSAGE("Redirecting legacy Nexon URL to EverLeaf");
    return g_ShellExecuteW(hwnd, operation, target, parameters, directory, showCmd);
}
} // namespace

void AttachEverLeafWebLinksMod() {
    bool ok = true;
    if (g_ShellExecuteA) ok = AttachHook(reinterpret_cast<void**>(&g_ShellExecuteA), reinterpret_cast<void*>(&ShellExecuteA_hook)) && ok;
    else ok = false;
    if (g_ShellExecuteW) ok = AttachHook(reinterpret_cast<void**>(&g_ShellExecuteW), reinterpret_cast<void*>(&ShellExecuteW_hook)) && ok;
    else ok = false;
    if (!ok) DEBUG_MESSAGE("EverLeaf web-link routing hook unavailable");
}
