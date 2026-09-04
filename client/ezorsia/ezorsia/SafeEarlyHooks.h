#pragma once

// Safer replacements for two inherited process-wide hooks. This header is
// intentionally included only by dllmain.cpp after ReplacementFuncs.h so it can
// reuse the established hook/type definitions without editing the legacy file.
namespace EverLeafEarlyHooks {
namespace detail {

static decltype(&CreateWindowExA) gCreateWindowExAOriginal = &CreateWindowExA;
static WSPStartup_t gWSPStartupOriginal =
    reinterpret_cast<WSPStartup_t>(GetFuncAddress("MSWSOCK", "WSPStartup"));
static sockaddr_in gOriginalGameEndpoint = {};
static bool gHaveOriginalGameEndpoint = false;

inline bool IsNamedWindowClass(LPCSTR className, const char* expected) {
    if (!className || IS_INTRESOURCE(className) || !expected) {
        return false;
    }
    return lstrcmpA(className, expected) == 0;
}

inline bool IsLegacyLoginAddress(const sockaddr_in& endpoint) {
    const ULONG address = endpoint.sin_addr.S_un.S_addr;
    return address == inet_addr("63.251.217.2") ||
           address == inet_addr("63.251.217.3") ||
           address == inet_addr("63.251.217.4");
}

inline HWND WINAPI CreateWindowExA_Hook(
    DWORD dwExStyle,
    LPCSTR lpClassName,
    LPCSTR lpWindowName,
    DWORD dwStyle,
    int X,
    int Y,
    int nWidth,
    int nHeight,
    HWND hWndParent,
    HMENU hMenu,
    HINSTANCE hInstance,
    LPVOID lpParam) {

    // lpClassName may legally be MAKEINTATOM(...). Never pass an atom/low-value
    // pointer to C string routines.
    if (IsNamedWindowClass(lpClassName, "MapleStoryClass")) {
        dwStyle |= WS_MINIMIZEBOX;
        return gCreateWindowExAOriginal(
            dwExStyle,
            lpClassName,
            "EverLeaf",
            dwStyle,
            X,
            Y,
            nWidth,
            nHeight,
            hWndParent,
            hMenu,
            hInstance,
            lpParam);
    }

    if (IsNamedWindowClass(lpClassName, "StartUpDlgClass")) {
        return nullptr;
    }

    return gCreateWindowExAOriginal(
        dwExStyle,
        lpClassName,
        lpWindowName,
        dwStyle,
        X,
        Y,
        nWidth,
        nHeight,
        hWndParent,
        hMenu,
        hInstance,
        lpParam);
}

inline INT WSPAPI WSPConnect_Hook(
    SOCKET s,
    const struct sockaddr* name,
    int namelen,
    LPWSABUF lpCallerData,
    LPWSABUF lpCalleeData,
    LPQOS lpSQOS,
    LPQOS lpGQOS,
    LPINT lpErrno) {

    const sockaddr* forwardedName = name;
    sockaddr_in redirected = {};
    bool redirectedLogin = false;

    // Do not mutate the caller-owned const sockaddr and do not depend on
    // WSAAddressToStringA/scratch-buffer success just to identify three IPv4s.
    if (name && namelen >= static_cast<int>(sizeof(sockaddr_in)) &&
        name->sa_family == AF_INET) {
        const sockaddr_in* endpoint = reinterpret_cast<const sockaddr_in*>(name);
        if (IsLegacyLoginAddress(*endpoint)) {
            redirected = *endpoint;
            gOriginalGameEndpoint = *endpoint;
            gHaveOriginalGameEndpoint = true;
            redirected.sin_addr.S_un.S_addr = inet_addr(MainMain::m_sRedirectIP);
            forwardedName = reinterpret_cast<const sockaddr*>(&redirected);
            redirectedLogin = true;
            MainMain::m_GameSock = s;
        }
    }

    const INT result = MainMain::m_ProcTable.lpWSPConnect(
        s,
        forwardedName,
        namelen,
        lpCallerData,
        lpCalleeData,
        lpSQOS,
        lpGQOS,
        lpErrno);

    // Keep the same asynchronous-connect tracking behavior as the inherited
    // hook. A provider may return SOCKET_ERROR/WSAEWOULDBLOCK while connection
    // establishment is still valid, so do not clear m_GameSock here.
    (void)redirectedLogin;
    return result;
}

inline INT WSPAPI WSPGetPeerName_Hook(
    SOCKET s,
    struct sockaddr* name,
    LPINT namelen,
    LPINT lpErrno) {

    const INT result = MainMain::m_ProcTable.lpWSPGetPeerName(s, name, namelen, lpErrno);
    if (result != SOCKET_ERROR &&
        s == MainMain::m_GameSock &&
        gHaveOriginalGameEndpoint &&
        name &&
        namelen &&
        *namelen >= static_cast<int>(sizeof(sockaddr_in)) &&
        name->sa_family == AF_INET) {
        sockaddr_in* endpoint = reinterpret_cast<sockaddr_in*>(name);
        endpoint->sin_addr = gOriginalGameEndpoint.sin_addr;
    }
    return result;
}

inline INT WSPAPI WSPCloseSocket_Hook(SOCKET s, LPINT lpErrno) {
    const INT result = MainMain::m_ProcTable.lpWSPCloseSocket(s, lpErrno);
    if (s == MainMain::m_GameSock) {
        MainMain::m_GameSock = INVALID_SOCKET;
        gHaveOriginalGameEndpoint = false;
        ZeroMemory(&gOriginalGameEndpoint, sizeof(gOriginalGameEndpoint));
    }
    return result;
}

inline INT WSPAPI WSPStartup_Hook(
    WORD wVersionRequested,
    LPWSPDATA lpWSPData,
    LPWSAPROTOCOL_INFOW lpProtocolInfo,
    WSPUPCALLTABLE UpcallTable,
    LPWSPPROC_TABLE lpProcTable) {

    if (!gWSPStartupOriginal) {
        return WSASYSCALLFAILURE;
    }

    const INT result = gWSPStartupOriginal(
        wVersionRequested,
        lpWSPData,
        lpProtocolInfo,
        UpcallTable,
        lpProcTable);

    if (result != NO_ERROR) {
        // Numeric stream insertion; never pointer arithmetic on a string literal.
        std::cout << "EverLeaf Client v2: WSPStartup error code: " << result << std::endl;
        return result;
    }

    if (!lpProcTable ||
        !lpProcTable->lpWSPConnect ||
        !lpProcTable->lpWSPGetPeerName ||
        !lpProcTable->lpWSPCloseSocket) {
        std::cout << "EverLeaf Client v2: WSPStartup returned an incomplete provider table" << std::endl;
        return WSASYSCALLFAILURE;
    }

    MainMain::m_GameSock = INVALID_SOCKET;
    MainMain::m_ProcTable = *lpProcTable;
    lpProcTable->lpWSPConnect = WSPConnect_Hook;
    lpProcTable->lpWSPGetPeerName = WSPGetPeerName_Hook;
    lpProcTable->lpWSPCloseSocket = WSPCloseSocket_Hook;
    return result;
}

} // namespace detail

inline bool HookCreateWindowExA(bool enable) {
    if (!detail::gCreateWindowExAOriginal) {
        return false;
    }
    return Memory::SetHook(
        enable,
        reinterpret_cast<void**>(&detail::gCreateWindowExAOriginal),
        reinterpret_cast<void*>(detail::CreateWindowExA_Hook));
}

inline bool HookWSPStartup(bool enable) {
    if (!detail::gWSPStartupOriginal) {
        return false;
    }
    return Memory::SetHook(
        enable,
        reinterpret_cast<void**>(&detail::gWSPStartupOriginal),
        reinterpret_cast<void*>(detail::WSPStartup_Hook));
}

} // namespace EverLeafEarlyHooks
