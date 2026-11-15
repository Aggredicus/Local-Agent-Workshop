#Requires -Version 5.1
# Online delivery qualification after the public ISO release. No mounting/WLAN.
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$temp=Join-Path ([IO.Path]::GetTempPath()) ('LAW ISO download '+[guid]::NewGuid().ToString('N'))
try {
    [IO.Directory]::CreateDirectory($temp) | Out-Null
    $process=New-Object Diagnostics.Process
    $process.StartInfo.FileName=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    $process.StartInfo.Arguments='-NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "'+(Join-Path $repo 'setup\usb\Prepare-USB.ps1')+'"'
    $process.StartInfo.UseShellExecute=$false
    $process.StartInfo.RedirectStandardInput=$true
    $process.StartInfo.RedirectStandardOutput=$true
    $process.StartInfo.RedirectStandardError=$true
    try {
        $process.Start() | Out-Null
        $stdout=$process.StandardOutput.ReadToEndAsync()
        $stderr=$process.StandardError.ReadToEndAsync()
        foreach ($answer in @('2',$temp,'','0')) {$process.StandardInput.WriteLine($answer)}
        $process.StandardInput.Close()
        if (-not $process.WaitForExit(480000)) {$process.Kill(); throw 'Real ISO download timed out.'}
        $text=$stdout.Result+$stderr.Result
        if ($process.ExitCode -ne 0 -or -not $text.Contains('Downloaded and SHA256 verified:')) {throw ('Windows ISO download failed: '+$text)}
        if ([regex]::Matches($text,'LAW shared USB:').Count -ne 2) {throw 'Successful download did not return to the menu.'}
    } finally {$process.Dispose()}
    $iso=Join-Path $temp 'LAW-Debian-13.7.0-amd64.iso'
    $hash=(Get-FileHash -LiteralPath $iso -Algorithm SHA256).Hash.ToLowerInvariant()
    if (-not [IO.File]::ReadAllText(($iso+'.sha256')).StartsWith($hash+'  ')) {throw 'Published Windows download checksum differs.'}
    Write-Host ('::notice::WINDOWS_ISO_DOWNLOAD_OK SHA256='+$hash)
} finally {
    if (Test-Path -LiteralPath $temp) {Remove-Item -LiteralPath $temp -Recurse -Force}
}
