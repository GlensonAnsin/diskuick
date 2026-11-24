# Builds dist\Diskuick.exe (single file, no console, no Python needed to run), plus:
#   - dist\Diskuick-portable-<version>.zip
#   - dist\Diskuick-Setup-<version>.exe   (only if Inno Setup's iscc.exe is installed)
# Optional code signing: set DISKUICK_SIGN_PFX (path) and DISKUICK_SIGN_PASSWORD, needs signtool.exe.
param([switch]$SkipTests)
Set-Location $PSScriptRoot
$py = ".\.venv\Scripts\python.exe"

if (-not (Test-Path .venv)) { python -m venv .venv }
& $py -m pip install --quiet -r requirements.txt

if (-not $SkipTests) {
    & $py -m unittest discover -s tests
    if ($LASTEXITCODE -ne 0) { Write-Error "Tests failed - not building."; exit 1 }
}

# PresentMon (MIT, Intel) measures the FPS shown in the overlay. It is downloaded once into vendor\ (not committed)
# and shipped next to Diskuick.exe. Set $presentMonSha256 to the hash printed on the first build to pin it.
$presentMonVersion = "2.6.0"
$presentMonSha256 = "b2a706bc6ad475749e3b7e3409263aa1e6906d45bdcf993f6dbc0f660188f1af"
$presentMon = "vendor\PresentMon.exe"
if (-not (Test-Path $presentMon)) {
    New-Item -ItemType Directory -Force vendor | Out-Null
    $url = "https://github.com/GameTechDev/PresentMon/releases/download/v$presentMonVersion/PresentMon-$presentMonVersion-x64.exe"
    Invoke-WebRequest $url -OutFile $presentMon
}
$hash = (Get-FileHash $presentMon -Algorithm SHA256).Hash.ToLower()
if ($presentMonSha256 -and $hash -ne $presentMonSha256.ToLower()) {
    Remove-Item $presentMon
    Write-Error "PresentMon hash mismatch ($hash) - deleted it, not building."; exit 1
}
if (-not $presentMonSha256) { Write-Host "PresentMon.exe sha256: $hash  (pin it in build.ps1 `$presentMonSha256)" }

$version = (& $py -c "from version import VERSION; print(VERSION)").Trim()
& $py make_icon.py
& $py -m PyInstaller --noconfirm --clean --onefile --noconsole `
    --icon assets\diskuick.ico --collect-all customtkinter --name Diskuick diskuick_tray.py
if ($LASTEXITCODE -ne 0) { Write-Error "PyInstaller failed ($LASTEXITCODE)"; exit 1 }

if ($env:DISKUICK_SIGN_PFX) {
    $signtool = (Get-Command signtool.exe -ErrorAction SilentlyContinue).Source
    if ($signtool) {
        & $signtool sign /f $env:DISKUICK_SIGN_PFX /p $env:DISKUICK_SIGN_PASSWORD `
            /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist\Diskuick.exe
    } else { Write-Warning "DISKUICK_SIGN_PFX is set but signtool.exe was not found - exe is UNSIGNED." }
}

$zip = "dist\Diskuick-portable-$version.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path dist\Diskuick.exe, $presentMon, README.md -DestinationPath $zip

$iscc = (Get-Command iscc.exe -ErrorAction SilentlyContinue).Source
if (-not $iscc) {
    $iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
              "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if ($iscc -and (Test-Path $iscc)) {
    & $iscc "/DAppVersion=$version" installer.iss
} else { Write-Host "Inno Setup not found - skipped installer (install it from jrsoftware.org to build one)." }

$setup = "dist\Diskuick-Setup-$version.exe"
if (Test-Path $setup) {
    $hash = (Get-FileHash $setup -Algorithm SHA256).Hash.ToLower()
    "$hash  Diskuick-Setup-$version.exe" | Set-Content "$setup.sha256" -Encoding ascii
}

Write-Host "Built: $PSScriptRoot\dist\Diskuick.exe  (v$version)"
