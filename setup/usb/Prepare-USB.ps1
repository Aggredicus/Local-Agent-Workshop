#Requires -Version 5.1
[CmdletBinding()]
param([switch]$StageWindowsTools, [string]$USBRoot)
$ErrorActionPreference = 'Stop'
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$local = Join-Path $env:LOCALAPPDATA 'LocalAgentWorkshop\USBTools'
function Stage-Tools {
    if (Test-Path -LiteralPath $local) { throw 'Local Windows tools already exist. Preserve/review that installation before upgrading.' }
    Write-Host 'Stage only a tools ZIP whose SHA256 you compared with the independently supplied release hash.'
    if ((Read-Host 'Type VERIFIED to confirm you checked the ZIP hash') -cne 'VERIFIED') { throw 'Cancelled.' }
    New-Item -ItemType Directory -Path $local -Force | Out-Null
    # Use the new private per-user directory, not executable code from the returning USB.
    $acl = New-Object Security.AccessControl.DirectorySecurity
    $acl.SetAccessRuleProtection($true, $false)
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $rule = New-Object Security.AccessControl.FileSystemAccessRule($sid, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
    $acl.AddAccessRule($rule)
    Set-Acl -LiteralPath $local -AclObject $acl
    $destination = Join-Path $local 'setup\usb'
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    foreach ($name in @('Wifi-Capsule.ps1','Wifi-Capsule.cs','Prepare-USB.ps1','README.md')) {
        $file = Join-Path $PSScriptRoot $name
        if ((Get-Item -LiteralPath $file).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked source file rejected.' }
        Copy-Item -LiteralPath $file -Destination (Join-Path $destination $name)
    }
    $tool = Join-Path $PSScriptRoot 'tools\age.exe'
    if ((Get-FileHash -LiteralPath $tool -Algorithm SHA256).Hash -ine '2821a4ed191da07372acd302e5f6feae7a7985e285e1417765ebe74025af45f0') { throw 'Missing or changed age.exe. Use the verified complete tools package.' }
    New-Item -ItemType Directory -Path (Join-Path $destination 'tools') -Force | Out-Null
    Copy-Item -LiteralPath $tool -Destination (Join-Path $destination 'tools\age.exe')
    Write-Host ('Windows tools staged at: ' + $local)
}
try {
    if ($StageWindowsTools) { Stage-Tools; exit 0 }
    Write-Host 'LAW shared USB: Windows tools + Debian installer + offline network recovery'
    Write-Host '1  Stage trusted Windows tools locally (do this before entering credentials)'
    Write-Host '2  Open official Ventoy and Debian DVD-1 download pages'
    Write-Host '3  Copy LAW folder to an already prepared Ventoy DATA volume'
    Write-Host '4  Create encrypted Wi-Fi file using the LOCAL Windows tools'
    Write-Host '0  Exit'
    switch (Read-Host 'Choose') {
        '1' { Stage-Tools }
        '2' {
            Start-Process 'https://www.ventoy.net/en/download.html'
            Start-Process 'https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/'
            Write-Host 'Verify downloads using official instructions. Select Debian DVD-1 for installation without internet.'
            Write-Host 'Ventoy initialization erases the selected USB; this program does not perform it or select a disk.'
        }
        '3' {
            if (-not $USBRoot) { $USBRoot = Read-Host 'Ventoy DATA drive root, such as E:\' }
            if ($USBRoot -notmatch '^[D-Zd-z]:\\$' -or $USBRoot.Substring(0,2) -ieq $env:SystemDrive) { throw 'Choose a non-system drive root.' }
            $drive = New-Object IO.DriveInfo($USBRoot)
            if (-not $drive.IsReady -or $drive.DriveFormat -notin @('exFAT','NTFS')) { throw 'Use the Ventoy exFAT/NTFS DATA volume; DVD-1 may exceed FAT32 limits.' }
            $target = Join-Path $USBRoot 'LAW'
            if (Test-Path -LiteralPath $target) { throw 'LAW folder exists; preserve it before copying a new version.' }
            Write-Host ('Only a new LAW folder will be copied to ' + $USBRoot + '; no formatting or partition changes.')
            if ((Read-Host 'Type COPY to approve') -cne 'COPY') { throw 'Cancelled.' }
            $manifestPath = Join-Path $source 'USB-PAYLOAD.json'
            if (-not (Test-Path -LiteralPath $manifestPath)) { throw 'Use the verified prepared tools ZIP; a working checkout may contain private/unrelated files and is not copied.' }
            $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
            foreach ($entry in $manifest.files) {
                if ($entry.path -match '(^/|\\|(^|/)\.\.(/|$)|:)') { throw 'Unsafe payload path.' }
                $origin = Join-Path $source ($entry.path.Replace('/','\'))
                if ((Get-Item -LiteralPath $origin).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked payload rejected.' }
                if ((Get-FileHash -LiteralPath $origin -Algorithm SHA256).Hash -ine $entry.sha256) { throw 'Payload hash mismatch.' }
            }
            New-Item -ItemType Directory -Path $target | Out-Null
            foreach ($entry in $manifest.files) {
                $origin = Join-Path $source ($entry.path.Replace('/','\'))
                $destination = Join-Path $target ($entry.path.Replace('/','\'))
                New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($destination)) -Force | Out-Null
                [IO.File]::Copy($origin, $destination, $false)
                if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash -ine $entry.sha256) { throw 'USB copy integrity failure.' }
            }
            [IO.File]::Copy($manifestPath, (Join-Path $target 'USB-PAYLOAD.json'), $false)
            Write-Host 'Copy the separately verified Debian ISO to the Ventoy DATA volume too. Do not copy a private Debian key.'
        }
        '4' {
            $script = Join-Path $local 'setup\usb\Wifi-Capsule.ps1'
            if (-not (Test-Path -LiteralPath $script)) { throw 'Stage trusted Windows tools first.' }
            & $script
            if ($LASTEXITCODE -ne 0) { exit 1 }
        }
        '0' { exit 0 }
        default { throw 'Unknown selection.' }
    }
} catch {
    Write-Host ('USB setup stopped: ' + $_.Exception.Message)
    Write-Host 'No disk formatting, execution-policy bypass or elevated software installation was attempted.'
    exit 1
}
