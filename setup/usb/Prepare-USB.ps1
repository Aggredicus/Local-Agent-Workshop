#Requires -Version 5.1
[CmdletBinding()]
param([switch]$StageWindowsTools, [string]$USBRoot)
$ErrorActionPreference = 'Stop'
$source = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$local = Join-Path $env:LOCALAPPDATA 'LocalAgentWorkshop\USBTools'
$isoName = 'LAW-Debian-13.7.0-amd64.iso'
$desktopISO = Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) $isoName
function Confirm-ISO([string]$Path) {
    $hashPath = $Path + '.sha256'
    foreach ($file in @($Path, $hashPath)) {
        if (-not [IO.File]::Exists($file) -or ((Get-Item -LiteralPath $file).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'ISO/checksum missing or linked. Download with option 2 first.' }
    }
    $checksum = [IO.File]::ReadAllText($hashPath).Trim()
    if ($checksum -notmatch ('^([a-fA-F0-9]{64}) [ *]' + [regex]::Escape($isoName) + '$')) { throw 'Invalid ISO checksum file.' }
    $expected = $Matches[1]
    if ((Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash -ine $expected) { throw 'ISO checksum mismatch. Preserve it for diagnosis and download again to a new location.' }
    return $expected
}
function Get-LawISO {
    $destination = Read-Host ('ISO destination folder [Enter = Desktop: ' + [IO.Path]::GetDirectoryName($desktopISO) + ']')
    if ([string]::IsNullOrWhiteSpace($destination)) { $destination = [IO.Path]::GetDirectoryName($desktopISO) }
    $directory = Get-Item -LiteralPath $destination
    if (-not $directory.PSIsContainer -or ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Choose an existing regular folder.' }
    $target = Join-Path $directory.FullName $isoName
    if ((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath ($target+'.sha256'))) { throw 'ISO or checksum already exists; preserve it or choose a different destination.' }
    $oldTLS = [Net.ServicePointManager]::SecurityProtocol
    $scratch = Join-Path $directory.FullName ('.law-download-' + [guid]::NewGuid().ToString('N'))
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $headers = @{'Accept'='application/vnd.github+json'; 'User-Agent'='LAW-USB-Tools'}
        $releases = Invoke-RestMethod -Uri 'https://api.github.com/repos/Aggredicus/Local-Agent-Workshop/releases?per_page=100' -Headers $headers
        $release = $releases | Where-Object { -not $_.draft -and $_.tag_name -cmatch '^law-iso-[0-9a-f]{12}$' } | Sort-Object published_at -Descending | Select-Object -First 1
        if (-not $release) { throw 'No verified LAW ISO release is available yet. Check the GitHub Build LAW offline Debian ISO workflow.' }
        $assets = @{}
        foreach ($name in @($isoName, ($isoName+'.sha256'))) {
            $asset = @($release.assets | Where-Object { $_.name -ceq $name })
            if ($asset.Count -ne 1) { throw 'Release is missing an ISO/checksum asset.' }
            $expectedURL = 'https://github.com/Aggredicus/Local-Agent-Workshop/releases/download/' + $release.tag_name + '/' + $name
            if ($asset[0].browser_download_url -cne $expectedURL) { throw 'Unexpected release download origin.' }
            $assets[$name] = $expectedURL
        }
        [IO.Directory]::CreateDirectory($scratch) | Out-Null
        Write-Host ('Downloading verified offline installer from ' + $release.tag_name + '. This may take several minutes.')
        $client = New-Object Net.WebClient
        try {
            $client.Headers['User-Agent'] = 'LAW-USB-Tools'
            foreach ($name in @(($isoName+'.sha256'), $isoName)) { $client.DownloadFile($assets[$name], (Join-Path $scratch $name)) }
        } finally { $client.Dispose() }
        $hash = Confirm-ISO (Join-Path $scratch $isoName)
        # File.Move refuses to overwrite a file created while downloading.
        [IO.File]::Move((Join-Path $scratch ($isoName+'.sha256')), ($target+'.sha256'))
        [IO.File]::Move((Join-Path $scratch $isoName), $target)
        Write-Host ('Downloaded and SHA256 verified: ' + $target)
        Write-Host ('SHA256: ' + $hash)
        Write-Host 'Use option 3 to copy this ISO and LAW tools to an already prepared Ventoy USB.'
    } finally {
        [Net.ServicePointManager]::SecurityProtocol = $oldTLS
        if (Test-Path -LiteralPath $scratch) { Remove-Item -LiteralPath $scratch -Recurse -Force }
    }
}
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
    foreach ($name in @('Wifi-Capsule.ps1','Wifi-Capsule.cs','Prepare-USB.ps1','Start-USB.ps1','README.md')) {
        $file = Join-Path $PSScriptRoot $name
        if ((Get-Item -LiteralPath $file).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked source file rejected.' }
        Copy-Item -LiteralPath $file -Destination (Join-Path $destination $name)
    }
    $launcher = Join-Path $source 'START-USB.cmd'
    if ((Get-Item -LiteralPath $launcher).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked launcher rejected.' }
    Copy-Item -LiteralPath $launcher -Destination (Join-Path $local 'START-USB.cmd')
    $tool = Join-Path $PSScriptRoot 'tools\age.exe'
    if ((Get-FileHash -LiteralPath $tool -Algorithm SHA256).Hash -ine '2821a4ed191da07372acd302e5f6feae7a7985e285e1417765ebe74025af45f0') { throw 'Missing or changed age.exe. Use the verified complete tools package.' }
    New-Item -ItemType Directory -Path (Join-Path $destination 'tools') -Force | Out-Null
    Copy-Item -LiteralPath $tool -Destination (Join-Path $destination 'tools\age.exe')
    Write-Host ('Windows tools staged at: ' + $local)
    Write-Host 'For later Wi-Fi entry, run START-USB.cmd in that local folder and choose 4.'
}
if ($StageWindowsTools) {
    try { Stage-Tools; exit 0 }
    catch { Write-Host ('Windows staging stopped: ' + $_.Exception.Message); exit 1 }
}
while ($true) {
  try {
    Write-Host 'LAW shared USB: Windows tools + Debian installer + offline network recovery'
    Write-Host '1  Stage trusted Windows tools locally (do this before entering credentials)'
    Write-Host '2  Download the tested custom offline Debian + LAW ISO to Desktop'
    Write-Host '3  Copy the ISO and LAW tools to an already prepared Ventoy USB'
    Write-Host '4  Create encrypted Wi-Fi file using the LOCAL Windows tools'
    Write-Host '0  Exit'
    $choice = Read-Host 'Choose'
    if ([string]::IsNullOrWhiteSpace($choice) -and [Console]::IsInputRedirected) { exit 0 }
    switch ($choice) {
        '1' { Stage-Tools }
        '2' { Get-LawISO }
        '3' {
            if (-not $USBRoot) { $USBRoot = Read-Host 'Ventoy DATA drive root, such as E:\' }
            if ($USBRoot -notmatch '^[D-Zd-z]:\\$' -or $USBRoot.Substring(0,2) -ieq $env:SystemDrive) { throw 'Choose a non-system drive root.' }
            $drive = New-Object IO.DriveInfo($USBRoot)
            if (-not $drive.IsReady -or $drive.DriveFormat -notin @('exFAT','NTFS')) { throw 'Use the Ventoy exFAT/NTFS DATA volume; DVD-1 may exceed FAT32 limits.' }
            $target = Join-Path $USBRoot 'LAW'
            if (Test-Path -LiteralPath $target) { throw 'LAW folder exists; preserve it before copying a new version.' }
            $isoPath = Read-Host ('Downloaded LAW ISO path [Enter = ' + $desktopISO + ']')
            if ([string]::IsNullOrWhiteSpace($isoPath)) { $isoPath = $desktopISO }
            $isoHash = Confirm-ISO $isoPath
            $isoTarget = Join-Path $USBRoot $isoName
            if ((Test-Path -LiteralPath $isoTarget) -or (Test-Path -LiteralPath ($isoTarget+'.sha256'))) { throw 'USB already contains this ISO/checksum; existing files preserved.' }
            Write-Host ('A new LAW folder and the verified ISO will be copied to ' + $USBRoot + '; no formatting or partition changes.')
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
            [IO.File]::Copy($isoPath, $isoTarget, $false)
            [IO.File]::Copy(($isoPath+'.sha256'), ($isoTarget+'.sha256'), $false)
            if ((Confirm-ISO $isoTarget) -ine $isoHash) { throw 'USB ISO copy integrity failure.' }
            Write-Host 'USB copy verified. Boot ThinkCentre2 from Ventoy and select the LAW ISO. Confirm the target disk in Debian Installer.'
        }
        '4' {
            $script = Join-Path $local 'setup\usb\Wifi-Capsule.ps1'
            if (-not (Test-Path -LiteralPath $script)) { throw 'Stage trusted Windows tools first.' }
            $shell = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
            & $shell -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File $script
            if ($LASTEXITCODE -ne 0) { throw 'Wi-Fi export did not complete. The menu remains available.' }
        }
        '0' { exit 0 }
        default { throw 'Unknown selection.' }
    }
  } catch {
    Write-Host ('USB setup stopped: ' + $_.Exception.Message)
    Write-Host 'No disk formatting, execution-policy bypass or elevated software installation was attempted.'
  }
  [void](Read-Host 'Press Enter to return to the menu')
}
