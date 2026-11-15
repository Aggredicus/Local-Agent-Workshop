#Requires -Version 5.1
# Native Windows integration test: only stub tools run, never WLAN or USB writes.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSEdition -ne 'Desktop' -or $PSVersionTable.PSVersion.Major -ne 5) {
    throw 'Run these tests with native Windows PowerShell 5.1.'
}
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$testRoot = Join-Path ([IO.Path]::GetTempPath()) ('LAW launcher ' + [guid]::NewGuid().ToString('N'))
$originalPolicies = Get-ExecutionPolicy -List | ConvertTo-Json -Compress

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}
function New-Fixture([string]$Name) {
    $root = Join-Path $testRoot ($Name + " O'Brien [brackets] & wow!")
    $scripts = Join-Path $root 'setup\usb'
    [IO.Directory]::CreateDirectory($scripts) | Out-Null
    Copy-Item -LiteralPath (Join-Path $repo 'START-USB.cmd') -Destination $root
    Copy-Item -LiteralPath (Join-Path $repo 'setup\usb\Start-USB.ps1') -Destination $scripts
    @'
$ErrorActionPreference = 'Stop'
@{
    process = [string](Get-ExecutionPolicy -Scope Process)
    user = [string](Get-ExecutionPolicy -Scope CurrentUser)
    machine = [string](Get-ExecutionPolicy -Scope LocalMachine)
    cwd = (Get-Location).Path
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'ran.json')
exit 0
'@ | Set-Content -LiteralPath (Join-Path $scripts 'Prepare-USB.ps1')
    "throw 'Wi-Fi script must not run during launcher tests.'" | Set-Content -LiteralPath (Join-Path $scripts 'Wifi-Capsule.ps1')
    "throw 'Unrelated script must never run.'" | Set-Content -LiteralPath (Join-Path $scripts 'Unrelated.ps1')
    foreach ($name in @('Start-USB.ps1', 'Prepare-USB.ps1', 'Wifi-Capsule.ps1', 'Unrelated.ps1')) {
        Set-Content -LiteralPath (Join-Path $scripts $name) -Stream Zone.Identifier -Value "[ZoneTransfer]`r`nZoneId=3"
    }
    return $root
}
function Invoke-Launcher([string]$Root, [string]$Answer) {
    $process = New-Object Diagnostics.Process
    $process.StartInfo.FileName = $env:ComSpec
    $process.StartInfo.Arguments = '/d /c ""' + (Join-Path $Root 'START-USB.cmd') + '""'
    $process.StartInfo.WorkingDirectory = $env:SystemRoot
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.RedirectStandardInput = $true
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    # Reproduce the user's default scripts-disabled policy in the launching process.
    $process.StartInfo.EnvironmentVariables['PSExecutionPolicyPreference'] = 'Restricted'
    $process.Start() | Out-Null
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.WriteLine($Answer)
    $process.StandardInput.Close()
    if (-not $process.WaitForExit(30000)) {
        $process.Kill()
        throw 'Launcher timed out.'
    }
    $result = @{code = $process.ExitCode; output = $stdout.Result + $stderr.Result}
    $process.Dispose()
    Write-Host $result.output
    return $result
}
function Has-Zone([string]$Path) {
    return $null -ne (Get-Item -LiteralPath $Path -Stream Zone.Identifier -ErrorAction SilentlyContinue)
}

try {
    $declined = New-Fixture 'declined'
    $result = Invoke-Launcher $declined 'N'
    Assert-True ($result.code -eq 0) ('Declining should exit successfully. ' + $result.output)
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $declined 'setup\usb\ran.json'))) 'Declining executed a script.'
    foreach ($name in @('Start-USB.ps1', 'Prepare-USB.ps1', 'Wifi-Capsule.ps1', 'Unrelated.ps1')) {
        Assert-True (Has-Zone (Join-Path $declined ('setup\usb\' + $name))) 'Declining changed a downloaded-file block.'
    }

    $approved = New-Fixture 'approved'
    $result = Invoke-Launcher $approved 'Y'
    Assert-True ($result.code -eq 0) ('Approved launcher failed. ' + $result.output)
    $ran = Get-Content -LiteralPath (Join-Path $approved 'setup\usb\ran.json') -Raw | ConvertFrom-Json
    Assert-True ($ran.process -eq 'RemoteSigned') 'Child did not use process-only RemoteSigned.'
    Assert-True ($ran.user -eq [string](Get-ExecutionPolicy -Scope CurrentUser)) 'CurrentUser policy changed.'
    Assert-True ($ran.machine -eq [string](Get-ExecutionPolicy -Scope LocalMachine)) 'LocalMachine policy changed.'
    Assert-True ($ran.cwd -ne $approved) 'Test must launch from a different working directory.'
    foreach ($name in @('Start-USB.ps1', 'Prepare-USB.ps1', 'Wifi-Capsule.ps1')) {
        Assert-True (-not (Has-Zone (Join-Path $approved ('setup\usb\' + $name)))) 'Approved script was not unblocked.'
    }
    Assert-True (Has-Zone (Join-Path $approved 'setup\usb\Unrelated.ps1')) 'Unrelated script was unblocked.'

    $incomplete = New-Fixture 'incomplete'
    Assert-True (Has-Zone (Join-Path $incomplete 'setup\usb\Prepare-USB.ps1')) 'Incomplete fixture lacks its initial zone marker.'
    Remove-Item -LiteralPath (Join-Path $incomplete 'setup\usb\Wifi-Capsule.ps1')
    Assert-True (Has-Zone (Join-Path $incomplete 'setup\usb\Prepare-USB.ps1')) 'Removing the other fixture file changed the zone marker.'
    $result = Invoke-Launcher $incomplete 'Y'
    Assert-True ($result.code -ne 0) 'Incomplete extraction falsely returned success.'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $incomplete 'setup\usb\ran.json'))) 'Incomplete extraction executed the menu.'
    Assert-True (Has-Zone (Join-Path $incomplete 'setup\usb\Prepare-USB.ps1')) ('Script changed before all required files were validated. ' + $result.output)
    Assert-True ((Get-ExecutionPolicy -List | ConvertTo-Json -Compress) -eq $originalPolicies) 'Parent policies changed.'
    Write-Host 'PASS: decline, restricted-policy launch, special-character paths, scoped unblocking, missing-file failure, unchanged saved policies.'
} finally {
    if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
}
