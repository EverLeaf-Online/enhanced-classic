#include "stdafx.h"
#include "EverLeafWebLinks.h"
#include "INIReader.h"
#include <shellapi.h>
#include <algorithm>
#include <cctype>
#include <string>

namespace {
    using ShellExecuteA_t = HINSTANCE(WINAPI*)(HWND, LPCSTR, LPCSTR, LPCSTR, LPCSTR, INT);
    using ShellExecuteW_t = HINSTANCE(WINAPI*)(HWND, LPCWSTR, LPCWSTR, LPCWSTR, LPCWSTR, INT);

    ShellExecuteA_t gShellExecuteA = ::ShellExecuteA;
    ShellExecuteW_t gShellExecuteW = ::ShellExecuteW;

    std::string GetBaseUrl() {
        INIReader config("config.ini");
        std::string base = config.Get("website", "BaseURL", "http://132.145.141.79");
        while (!base.empty() && base.back() == '/') {
            base.pop_back();
        }
        return base;
    }

    std::string ToLower(std::string value) {
        std::transform(value.begin(), value.end(), value.begin(), [](unsigned char c) {
            return static_cast<char>(std::tolower(c));
        });
        return value;
    }

    std::string RouteLegacyUrl(const char* rawUrl) {
        if (rawUrl == nullptr || *rawUrl == '\0') {
            return {};
        }

        const std::string original(rawUrl);
        const std::string url = ToLower(original);

        // Only rewrite legacy MapleStory/Nexon web destinations. Other programs/files
        // opened by the client are deliberately left untouched.
        const bool mapleLink =
            url.find("maplestory") != std::string::npos ||
            url.find("nexon") != std::string::npos ||
            url.find("maple") != std::string::npos;

        if (!mapleLink) {
            return original;
        }

        const std::string base = GetBaseUrl();
        if (url.find("register") != std::string::npos ||
            url.find("signup") != std::string::npos ||
            url.find("sign-up") != std::string::npos) {
            return base + "/register";
        }

        // The CMS currently supports authenticated password changes, but it does not
        // yet have public forgot-ID/forgot-password routes. Route those old buttons
        // to EverLeaf Support rather than sending players to dead Nexon pages.
        if (url.find("password") != std::string::npos ||
            url.find("passwd") != std::string::npos ||
            url.find("forgot") != std::string::npos ||
            url.find("findid") != std::string::npos ||
            url.find("find_id") != std::string::npos ||
            url.find("find-id") != std::string::npos ||
            url.find("account") != std::string::npos) {
            return base + "/support";
        }

        return base + "/";
    }

    std::wstring RouteLegacyUrl(const wchar_t* rawUrl) {
        if (rawUrl == nullptr || *rawUrl == L'\0') {
            return {};
        }

        const int required = WideCharToMultiByte(CP_UTF8, 0, rawUrl, -1, nullptr, 0, nullptr, nullptr);
        if (required <= 1) {
            return rawUrl;
        }

        std::string utf8(static_cast<size_t>(required), '\0');
        WideCharToMultiByte(CP_UTF8, 0, rawUrl, -1, utf8.data(), required, nullptr, nullptr);
        utf8.resize(static_cast<size_t>(required - 1));
        const std::string routed = RouteLegacyUrl(utf8.c_str());

        const int wideRequired = MultiByteToWideChar(CP_UTF8, 0, routed.c_str(), -1, nullptr, 0);
        if (wideRequired <= 1) {
            return rawUrl;
        }

        std::wstring result(static_cast<size_t>(wideRequired), L'\0');
        MultiByteToWideChar(CP_UTF8, 0, routed.c_str(), -1, result.data(), wideRequired);
        result.resize(static_cast<size_t>(wideRequired - 1));
        return result;
    }

    HINSTANCE WINAPI ShellExecuteA_Hook(HWND hwnd, LPCSTR operation, LPCSTR file,
                                        LPCSTR parameters, LPCSTR directory, INT showCmd) {
        const std::string routed = RouteLegacyUrl(file);
        return gShellExecuteA(hwnd, operation, routed.empty() ? file : routed.c_str(), parameters, directory, showCmd);
    }

    HINSTANCE WINAPI ShellExecuteW_Hook(HWND hwnd, LPCWSTR operation, LPCWSTR file,
                                        LPCWSTR parameters, LPCWSTR directory, INT showCmd) {
        const std::wstring routed = RouteLegacyUrl(file);
        return gShellExecuteW(hwnd, operation, routed.empty() ? file : routed.c_str(), parameters, directory, showCmd);
    }
}

bool EverLeafWebLinks::Install() {
    bool ok = true;
    ok &= Memory::SetHook(true, reinterpret_cast<void**>(&gShellExecuteA), reinterpret_cast<void*>(&ShellExecuteA_Hook));
    ok &= Memory::SetHook(true, reinterpret_cast<void**>(&gShellExecuteW), reinterpret_cast<void*>(&ShellExecuteW_Hook));
    return ok;
}

namespace {
    // This translation unit is included by stdafx.cpp so it remains part of the
    // existing Visual Studio project without requiring users to repair project files.
    // The DLL already installs Windows API detours during process attach; doing the
    // same here makes the legacy login web buttons available before the login UI runs.
    struct EverLeafWebLinkBootstrap {
        EverLeafWebLinkBootstrap() {
            EverLeafWebLinks::Install();
        }
    } gEverLeafWebLinkBootstrap;
}
