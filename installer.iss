; Inno Setup script for Diskuick. Build with:  iscc /DAppVersion=1.2.0 installer.iss
; (build.ps1 does this automatically when Inno Setup is installed.)
; Tested: silent install/uninstall, shortcut, optional startup entry and cleanup all verified.
#ifndef AppVersion
  #define AppVersion "1.2.0"
#endif

[Setup]
AppId={{B6D8D1A2-5C58-4E0B-9A39-2D6D1F6B7C11}
AppName=Diskuick
AppVersion={#AppVersion}
AppPublisher=Diskuick
DefaultDirName={localappdata}\Programs\Diskuick
DefaultGroupName=Diskuick
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=Diskuick-Setup-{#AppVersion}
SetupIconFile=assets\diskuick.ico
UninstallDisplayIcon={app}\Diskuick.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
; Windows' Restart Manager can't close a PyInstaller one-file exe (its launcher has no window),
; so the [Code] section below stops a running Diskuick itself instead.
CloseApplications=no
RestartApplications=no

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
Name: "startup"; Description: "Start Diskuick when I sign in to Windows"; Flags: checkedonce

[Files]
Source: "dist\Diskuick.exe"; DestDir: "{app}"; Flags: ignoreversion
; Intel PresentMon (MIT), used for the overlay's FPS counter. Fetched by build.ps1 into vendor\.
Source: "vendor\PresentMon.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Diskuick"; Filename: "{app}\Diskuick.exe"
Name: "{autodesktop}\Diskuick"; Filename: "{app}\Diskuick.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Diskuick"; ValueData: """{app}\Diskuick.exe"""; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\Diskuick.exe"; Description: "Launch Diskuick"; Flags: nowait postinstall skipifsilent

; Used by the in-app updater (passes /RELAUNCH=1 so the app comes back after a silent upgrade).
Filename: "{app}\Diskuick.exe"; Flags: nowait runasoriginaluser; Check: ShouldRelaunch

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\diskuick"

[Code]
// Windows API used to wait for the old Diskuick process to exit (in-app updates pass /WAITPID=<pid>)
function OpenProcess(dwDesiredAccess: DWORD; bInheritHandle: BOOL; dwProcessId: DWORD): THandle;
  external 'OpenProcess@kernel32.dll stdcall';
function WaitForSingleObject(hHandle: THandle; dwMilliseconds: DWORD): DWORD;
  external 'WaitForSingleObject@kernel32.dll stdcall';
function CloseHandle(hObject: THandle): BOOL;
  external 'CloseHandle@kernel32.dll stdcall';

procedure StopRunningApp;
var
  rc: Integer;
  ok: Boolean;
begin
  ok := Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /T /IM Diskuick.exe', '', SW_HIDE, ewWaitUntilTerminated, rc);
  Log('StopRunningApp: Exec=' + IntToStr(Ord(ok)) + ' exitcode=' + IntToStr(rc));
  Sleep(1000);
end;

function InitializeUninstall: Boolean;
begin
  StopRunningApp;
  Result := True;
end;

function InitializeSetup: Boolean;
var
  pid: Integer;
  h: THandle;
begin
  Result := True;
  pid := StrToIntDef(ExpandConstant('{param:WAITPID|0}'), 0);
  if pid > 0 then
  begin
    h := OpenProcess($00100000, False, pid);  // SYNCHRONIZE
    if h <> 0 then
    begin
      WaitForSingleObject(h, 20000);
      CloseHandle(h);
    end;
    Sleep(1500);  // let the PyInstaller launcher process release the exe as well
  end;
  StopRunningApp;  // manual upgrade while Diskuick is running: close it, then install
end;

function ShouldRelaunch: Boolean;
begin
  Result := ExpandConstant('{param:RELAUNCH|0}') = '1';
end;
