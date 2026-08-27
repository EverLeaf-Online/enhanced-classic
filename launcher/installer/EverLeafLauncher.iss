#define MyAppName "EverLeaf Launcher"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "EverLeaf"
#define MyAppExeName "EverLeafLauncher.exe"

[Setup]
AppId={{9A774437-E431-44F2-8A2A-2F7B8AA1FC19}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={userdocs}\EverLeaf
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
function NextButtonClick(CurPageID: Integer): Boolean;
var
  GameExe: String;
begin
  Result := True;
  if CurPageID = wpSelectDir then
  begin
    GameExe := AddBackslash(WizardDirValue) + 'MapleStory.exe';
    if not FileExists(GameExe) then
    begin
      MsgBox(
        'Select your supported MapleStory v83 / EverLeaf game folder.' + #13#10 + #13#10 +
        'MapleStory.exe must already be present in the selected folder. The launcher does not install the base game client.',
        mbError, MB_OK);
      Result := False;
    end;
  end;
end;
