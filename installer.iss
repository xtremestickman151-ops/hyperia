#define MyVer "1.1.7"
[Setup]
AppId={{B2C3D4E5-F6A7-8901-BCDE-HYPERIA00001}}
AppName=HYPERIA
AppVersion={#MyVer}
AppVerName=HYPERIA {#MyVer}
AppPublisher=EX Inc.
AppPublisherURL=https://github.com/xtremestickman151-ops/hyperia
AppCopyright=©2026 EX Inc.
VersionInfoVersion={#MyVer}.0
VersionInfoCompany=EX Inc.
VersionInfoCopyright=©2026 EX Inc.
VersionInfoProductName=HYPERIA
VersionInfoDescription=HYPERIA Setup
DefaultDirName={localappdata}\Programs\HYPERIA
DefaultGroupName=HYPERIA
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=HYPERIA Setup {#MyVer}
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\HYPERIA.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "dist\HYPERIA\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\HYPERIA"; Filename: "{app}\HYPERIA.exe"
Name: "{group}\Uninstall HYPERIA"; Filename: "{uninstallexe}"
Name: "{userdesktop}\HYPERIA"; Filename: "{app}\HYPERIA.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\HYPERIA.exe"; Description: "Launch HYPERIA now"; Flags: nowait postinstall skipifsilent
