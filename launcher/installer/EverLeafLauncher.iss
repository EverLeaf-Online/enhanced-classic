#define MyAppName "EverLeaf Launcher"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "EverLeaf"
#define MyAppExeName "EverLeafLauncher.exe"

[Setup]
AppId={{9A774437-E431-44F2-8A2A-2F7B8AA1FC19}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={code:GetDefaultGameDir}
UsePreviousAppDir=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\..\launcher-installer
OutputBaseFilename=EverLeafLauncherSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "..\..\launcher-publish\EverLeafLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; DestName: "README-LAUNCHER.md"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\EverLeaf Launcher"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{userdesktop}\EverLeaf Launcher"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch EverLeaf"; Flags: nowait postinstall skipifsilent

[Code]
function IsGameDir(Dir: String): Boolean;
begin
  Result :=
    FileExists(AddBackslash(Dir) + 'EverLeaf.exe') or
    FileExists(AddBackslash(Dir) + 'MapleStory.exe');
end;

function GetDefaultGameDir(Param: String): String;
var
  Candidate: String;
begin
  Candidate := ExpandConstant('{userdocs}\EverLeaf');
  if IsGameDir(Candidate) then begin Result := Candidate; Exit; end;
  Candidate := 'C:\Nexon\MapleStory';
  if IsGameDir(Candidate) then begin Result := Candidate; Exit; end;
  Candidate := ExpandConstant('{pf32}\Wizet\MapleStory');
  if IsGameDir(Candidate) then begin Result := Candidate; Exit; end;
  Candidate := ExpandConstant('{pf32}\Nexon\MapleStory');
  if IsGameDir(Candidate) then begin Result := Candidate; Exit; end;
  Result := ExpandConstant('{userdocs}\EverLeaf');
end;
