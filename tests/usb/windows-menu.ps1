#Requires -Version 5.1
# Exercise the real looping menu with isolated files; no Wi-Fi or USB device.
param([Parameter(Mandatory=$true)][string]$AgePath)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$temp = Join-Path ([IO.Path]::GetTempPath()) ("LAW menu O'Brien [test] " + [guid]::NewGuid().ToString('N'))
try {
    $source = Join-Path $temp 'source'
    $scripts = Join-Path $source 'setup\usb'
    [IO.Directory]::CreateDirectory((Join-Path $scripts 'tools')) | Out-Null
    foreach ($name in @('Prepare-USB.ps1','Start-USB.ps1','Wifi-Capsule.cs','README.md')) {
        [IO.File]::Copy((Join-Path $repo ('setup\usb\'+$name)), (Join-Path $scripts $name))
    }
    [IO.File]::Copy((Join-Path $repo 'START-USB.cmd'), (Join-Path $source 'START-USB.cmd'))
    [IO.File]::Copy($AgePath, (Join-Path $scripts 'tools\age.exe'))
    @'
$marker=Join-Path $PSScriptRoot 'synthetic-wifi-ran.txt'
if (Test-Path -LiteralPath $marker) { exit 7 }
Set-Content -LiteralPath $marker -Value 'Synthetic child completed.'
Write-Host 'SYNTHETIC_WIFI_SUCCESS'
exit 0
'@ | Set-Content -LiteralPath (Join-Path $scripts 'Wifi-Capsule.ps1')
    $wrapper = Join-Path $temp 'test-wrapper.ps1'
    @'
param([string]$Root)
$ErrorActionPreference='Stop'
$env:LOCALAPPDATA=Join-Path $Root 'isolated-appdata'
$answers=New-Object 'Collections.Generic.Queue[string]'
# Stage succeeds; repeat fails; download has no release; invalid drive fails;
# Wi-Fi child succeeds then fails. Every case must return to the real menu.
@('1','VERIFIED','','1','','2','','','3','C:\','','4','','4','','0') | ForEach-Object {$answers.Enqueue($_)}
function Read-Host([string]$Prompt) {
    if ($answers.Count -eq 0) {throw 'Unexpected menu prompt.'}
    return $answers.Dequeue()
}
function Invoke-RestMethod { return @() }
& (Join-Path $Root 'source\setup\usb\Prepare-USB.ps1')
'@ | Set-Content -LiteralPath $wrapper
    $process = New-Object Diagnostics.Process
    $process.StartInfo.FileName = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    $process.StartInfo.Arguments = '-NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "'+$wrapper+'" -Root "'+$temp+'"'
    $process.StartInfo.UseShellExecute=$false
    $process.StartInfo.RedirectStandardOutput=$true
    $process.StartInfo.RedirectStandardError=$true
    try {
        $process.Start() | Out-Null
        $stdout=$process.StandardOutput.ReadToEndAsync()
        $stderr=$process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(30000)) {$process.Kill(); throw 'Menu loop timed out.'}
        $text=$stdout.Result+$stderr.Result
        if ($process.ExitCode -ne 0) {throw ('Menu test failed: '+$text)}
        if ([regex]::Matches($text,'LAW shared USB:').Count -ne 7) {throw ('An action did not return to the menu: '+$text)}
        foreach ($expected in @('Windows tools staged at:', 'already exist', 'No verified LAW ISO release', 'Choose a non-system drive', 'SYNTHETIC_WIFI_SUCCESS', 'Wi-Fi export did not complete')) {
            if (-not $text.Contains($expected)) {throw ('Missing action result '+$expected+': '+$text)}
        }
    } finally {$process.Dispose()}
    Write-Host 'PASS: real menu returns after staging success/failure, ISO failure, drive rejection, and Wi-Fi child success/failure; only 0 exits.'
} finally {
    if (Test-Path -LiteralPath $temp) {Remove-Item -LiteralPath $temp -Recurse -Force}
}
