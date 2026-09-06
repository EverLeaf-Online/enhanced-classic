#define EVERLEAF_PRESENCE_TEST
#include <windows.h>
#include <cassert>
#include <iostream>
#include <string>
struct INIReader { explicit INIReader(const char*) {} bool GetBoolean(const char*,const char*,bool v) { return v; } };
namespace CrashDiagnostics { void LogEvent(const char*) {} }
#include "../ezorsia/ezorsia/DiscordPresence.cpp"
using namespace DiscordPresence;
std::vector<BYTE> Frame(Opcode opcode,const std::string& body) {
 FrameHeader h{static_cast<std::uint32_t>(opcode),static_cast<std::uint32_t>(body.size())};
 std::vector<BYTE> b(sizeof(h)+body.size());std::memcpy(b.data(),&h,sizeof(h));std::memcpy(b.data()+sizeof(h),body.data(),body.size());return b;
}
int main() {
 SetActivity("Playing \"EverLeaf\"\nwith friends","Enhanced classic adventure");
 std::cout << BuildActivity("test-nonce") << std::endl;
 Incoming incoming;
 auto ready=Frame(Opcode::Frame,R"({"cmd":"DISPATCH","evt" : "READY"})");
 incoming.bytes.assign(ready.begin(),ready.begin()+3);
 assert(ProcessIncoming(INVALID_HANDLE_VALUE,incoming,""));assert(!incoming.ready);
 incoming.bytes.insert(incoming.bytes.end(),ready.begin()+3,ready.end());
 assert(ProcessIncoming(INVALID_HANDLE_VALUE,incoming,""));assert(incoming.ready);
 incoming.bytes=Frame(Opcode::Frame,R"({"cmd":"SET_ACTIVITY","nonce":"wrong","evt":null})");
 assert(ProcessIncoming(INVALID_HANDLE_VALUE,incoming,"expected"));assert(!incoming.acknowledged);
 incoming.bytes=Frame(Opcode::Frame,R"({"cmd":"SET_ACTIVITY","nonce":"expected","evt":null})");
 assert(ProcessIncoming(INVALID_HANDLE_VALUE,incoming,"expected"));assert(incoming.acknowledged);
 incoming.bytes=Frame(Opcode::Frame,R"({"evt":"ERROR","data":{"code":4000}})");
 assert(!ProcessIncoming(INVALID_HANDLE_VALUE,incoming,"expected"));
 incoming.bytes=Frame(Opcode::Close,"{}");assert(!ProcessIncoming(INVALID_HANDLE_VALUE,incoming,""));
 FrameHeader tooLarge{1,65537};incoming.bytes.resize(sizeof(tooLarge));std::memcpy(incoming.bytes.data(),&tooLarge,sizeof(tooLarge));
 assert(!ProcessIncoming(INVALID_HANDLE_VALUE,incoming,""));
 const std::wstring name=L"\\\\.\\pipe\\everleaf-presence-test-"+std::to_wstring(GetCurrentProcessId());
 HANDLE server=CreateNamedPipeW(name.c_str(),PIPE_ACCESS_DUPLEX,PIPE_TYPE_BYTE|PIPE_READMODE_BYTE|PIPE_WAIT,1,65536,65536,0,nullptr);
 assert(server!=INVALID_HANDLE_VALUE);
 HANDLE client=CreateFileW(name.c_str(),GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_EXISTING,FILE_FLAG_OVERLAPPED,nullptr);
 assert(client!=INVALID_HANDLE_VALUE);
 assert(ConnectNamedPipe(server,nullptr)||GetLastError()==ERROR_PIPE_CONNECTED);
 incoming.bytes=Frame(Opcode::Ping,"heartbeat");
 assert(ProcessIncoming(client,incoming,""));
 BYTE bytes[128];DWORD read=0;assert(ReadFile(server,bytes,sizeof(bytes),&read,nullptr));
 FrameHeader pong{};std::memcpy(&pong,bytes,sizeof(pong));
 assert(pong.opcode==4&&pong.length==9);
 assert(std::string(reinterpret_cast<char*>(bytes+sizeof(pong)),9)=="heartbeat");
 CloseHandle(server);
 assert(!PollPipe(client,incoming,""));
 CloseHandle(client);
}
