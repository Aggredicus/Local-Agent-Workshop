#Requires -Version 5.1
# Exercise the real staging entrypoint in a disposable child-process profile.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$AgePath)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$temp = Join-Path ([IO.Path]::GetTempPath()) ("LAW staging O'Brien [test] " + [guid]::NewGuid().ToString('N'))
$source = Join-Path $temp 'source'
$profile = Join-Path $temp 'isolated-appdata'
$target = Join-Path $profile 'LocalAgentWorkshop\USBTools'

function Invoke-Preparation([string]$Script, [bool]$Stage) {
    $process = New-Object Diagnostics.Process
    $process.StartInfo.FileName = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    $process.StartInfo.Arguments = '-NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "' + $Script + '"'
    if ($Stage) { $process.StartInfo.Arguments += ' -StageWindowsTools' }
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.RedirectStandardInput = $true
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    # Only the disposable child gets this path; the user's profile is untouched.
    $process.StartInfo.EnvironmentVariables['LOCALAPPDATA'] = $profile
    try {
        $process.Start() | Out-Null
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if ($Stage) { $process.StandardInput.WriteLine('VERIFIED') }
        else { $process.StandardInput.WriteLine('0') }
        $process.StandardInput.Close()
        if (-not $process.WaitForExit(30000)) { $process.Kill(); throw 'Staging test timed out.' }
        return @{code=$process.ExitCode; output=$stdout.Result+$stderr.Result}
    } finally { $process.Dispose() }
}

try {
    $scripts = Join-Path $source 'setup\usb'
    [IO.Directory]::CreateDirectory((Join-Path $scripts 'tools')) | Out-Null
    foreach ($name in @('Start-USB.ps1','Prepare-USB.ps1','Wifi-Capsule.ps1','Wifi-Capsule.cs','README.md')) {
        [IO.File]::Copy((Join-Path $repo ('setup\usb\'+$name)), (Join-Path $scripts $name))
    }
    [IO.File]::Copy((Join-Path $repo 'START-USB.cmd'), (Join-Path $source 'START-USB.cmd'))
    [IO.File]::Copy($AgePath, (Join-Path $scripts 'tools\age.exe'))
    $result = Invoke-Preparation (Join-Path $scripts 'Prepare-USB.ps1') $true
    if ($result.code -ne 0) { throw ('Real Windows staging failed: '+$result.output) }
    $acl = Get-Acl -LiteralPath $target
    if (-not $acl.AreAccessRulesProtected) { throw 'Staging directory inherited permissions.' }
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $rules = @($acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier]))
    if ($rules.Count -ne 1 -or $rules[0].IdentityReference -ne $sid -or $rules[0].AccessControlType -ne 'Allow' -or $rules[0].FileSystemRights -ne 'FullControl') {
        throw 'Staging directory was not restricted to its current user.'
    }
    $before = @{}
    foreach ($file in Get-ChildItem -LiteralPath $source -File -Recurse) {
        $relative = $file.FullName.Substring($source.Length+1)
        $copy = Join-Path $target $relative
        $expected = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        if ((Get-FileHash -LiteralPath $copy -Algorithm SHA256).Hash -cne $expected) { throw 'Staged file differs from verified source.' }
        $before[$relative] = $expected
    }
    $again = Invoke-Preparation (Join-Path $scripts 'Prepare-USB.ps1') $true
    if ($again.code -eq 0) { throw 'Existing installation was silently replaced.' }
    foreach ($relative in $before.Keys) {
        if ((Get-FileHash -LiteralPath (Join-Path $target $relative) -Algorithm SHA256).Hash -cne $before[$relative]) { throw 'Repeated staging changed an existing file.' }
    }
    $menu = Invoke-Preparation (Join-Path $target 'setup\usb\Prepare-USB.ps1') $false
    if ($menu.code -ne 0) { throw ('Locally staged menu failed: '+$menu.output) }
    Write-Host 'PASS: real Windows staging, private owner ACL, exact copied tools, existing-install preservation, local menu.'
} finally {
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
