#Requires -Version 5.1
# Real option 3 on an isolated NTFS folder mapped to a temporary DOS drive.
# Never opens a block device, formats a disk, invokes WLAN, or uses real secrets.
$ErrorActionPreference='Stop'
if ($PSVersionTable.PSEdition -ne 'Desktop') {throw 'Run with native Windows PowerShell 5.1.'}
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$temp=Join-Path ([IO.Path]::GetTempPath()) ("LAW copy O'Brien [test] "+[guid]::NewGuid().ToString('N'))
$mapped=$false
$letter=$null
try {
    $source=Join-Path $temp 'source'
    $scripts=Join-Path $source 'setup\usb'
    $images=Join-Path $temp 'Documents\Linux Images\LAW Custom Images\LAW d.11152026 v1.0'
    $volume=Join-Path $temp 'isolated-ventoy-data'
    foreach ($directory in @($scripts,$images,$volume)) {[IO.Directory]::CreateDirectory($directory) | Out-Null}
    [IO.File]::Copy((Join-Path $repo 'setup\usb\Prepare-USB.ps1'),(Join-Path $scripts 'Prepare-USB.ps1'))
    [IO.File]::WriteAllText((Join-Path $source 'README.md'),'Synthetic trusted tool payload.')
    $entries=@()
    foreach ($name in @('setup/usb/Prepare-USB.ps1','README.md')) {
        $entries+=@{path=$name;sha256=(Get-FileHash -LiteralPath (Join-Path $source $name) -Algorithm SHA256).Hash}
    }
    [IO.File]::WriteAllText((Join-Path $source 'USB-PAYLOAD.json'),(@{format=1;files=$entries}|ConvertTo-Json -Depth 4))
    $isoName='LAW-Debian-13.7.0-amd64.iso'
    $iso=Join-Path $images $isoName
    [IO.File]::WriteAllText($iso,'Synthetic ISO for copy-flow testing only.')
    $hash=(Get-FileHash -LiteralPath $iso -Algorithm SHA256).Hash
    [IO.File]::WriteAllText(($iso+'.sha256'),($hash+'  '+$isoName+"`n"))
    $used=@([IO.Directory]::GetLogicalDrives())
    foreach ($candidate in @('Z','Y','X','W','V')) {
        if ($used -notcontains ($candidate+':\')) {$letter=$candidate;break}
    }
    if (-not $letter) {throw 'No unused DOS drive letter for the isolated copy test.'}
    & subst ($letter+':') $volume
    if ($LASTEXITCODE -ne 0) {throw 'Could not create temporary folder-only drive mapping.'}
    $mapped=$true
    $drive=$letter+':\'
    $process=New-Object Diagnostics.Process
    $process.StartInfo.FileName=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    $process.StartInfo.Arguments='-NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "'+(Join-Path $scripts 'Prepare-USB.ps1')+'" -USBRoot '+$drive
    $process.StartInfo.UseShellExecute=$false
    $process.StartInfo.RedirectStandardInput=$true
    $process.StartInfo.RedirectStandardOutput=$true
    $process.StartInfo.RedirectStandardError=$true
    $process.StartInfo.EnvironmentVariables['LOCALAPPDATA']=Join-Path $temp 'isolated-appdata'
    try {
        $process.Start() | Out-Null
        $stdout=$process.StandardOutput.ReadToEndAsync()
        $stderr=$process.StandardError.ReadToEndAsync()
        foreach ($answer in @('3',('"'+$images+'"'),'COPY','','3','','0')) {$process.StandardInput.WriteLine($answer)}
        $process.StandardInput.Close()
        if (-not $process.WaitForExit(30000)) {$process.Kill();throw 'Copy flow timed out.'}
        $text=$stdout.Result+$stderr.Result
        if ($process.ExitCode -ne 0 -or -not $text.Contains('USB copy verified.')) {throw ('Real option 3 failed: '+$text)}
        if (-not $text.Contains('LAW folder exists') -or [regex]::Matches($text,'LAW shared USB:').Count -ne 3) {throw ('Copy retry/persistent menu failed: '+$text)}
    } finally {$process.Dispose()}
    foreach ($entry in $entries) {
        if ((Get-FileHash -LiteralPath (Join-Path (Join-Path $volume 'LAW') $entry.path) -Algorithm SHA256).Hash -ine $entry.sha256) {throw 'Copied payload differs.'}
    }
    if ((Get-FileHash -LiteralPath (Join-Path $volume $isoName) -Algorithm SHA256).Hash -ine $hash) {throw 'Copied ISO differs.'}
    if (-not [IO.File]::ReadAllText((Join-Path $volume ($isoName+'.sha256'))).StartsWith($hash.ToLowerInvariant()+'  ')) {throw 'Copied ISO checksum is incorrect.'}
    Write-Host 'PASS: actual option 3, quoted Documents folder, full verified ISO/tool copy, existing-file preservation, and return to menu on an isolated NTFS mapping.'
} finally {
    if ($mapped) {& subst ($letter+':') /d}
    if (Test-Path -LiteralPath $temp) {Remove-Item -LiteralPath $temp -Recurse -Force}
}
