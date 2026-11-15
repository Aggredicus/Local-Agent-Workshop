#Requires -Version 5.1
# Disposable synthetic data only. No Wi-Fi APIs are invoked.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$temp = Join-Path ([IO.Path]::GetTempPath()) ("LAW crypto O'Brien [test] " + [guid]::NewGuid().ToString('N'))
$ssid = $null
$password = $null

function Invoke-Native([string]$Exe, [string[]]$Arguments) {
    # Arguments here are fixed test options and paths, never a key or password.
    if ($Arguments | Where-Object { $_.Contains('"') }) { throw 'Unexpected quote in test argument.' }
    $process = New-Object Diagnostics.Process
    $process.StartInfo.FileName = $Exe
    $process.StartInfo.Arguments = ($Arguments | ForEach-Object { '"' + $_ + '"' }) -join ' '
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.CreateNoWindow = $true
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    $process.StartInfo.StandardOutputEncoding = [Text.Encoding]::UTF8
    try {
        $process.Start() | Out-Null
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(30000)) { $process.Kill(); throw 'Native test operation timed out.' }
        if ($process.ExitCode -ne 0) { throw ('Native test operation failed: ' + $process.ExitCode) }
        $stderr.Result | Out-Null
        return $stdout.Result
    } finally { $process.Dispose() }
}

try {
    & (Join-Path $repo 'setup\usb\Wifi-Capsule.ps1') -CompileOnly
    if ($LASTEXITCODE -ne 0) { throw 'Production credential helper did not compile.' }
    [IO.Directory]::CreateDirectory($temp) | Out-Null
    $archive = Join-Path $temp 'age.zip'
    & curl.exe --fail --silent --show-error --location --proto '=https' --tlsv1.2 --max-time 90 'https://github.com/FiloSottile/age/releases/download/v1.3.2/age-v1.3.2-windows-amd64.zip' --output $archive
    if ($LASTEXITCODE -ne 0) { throw 'Pinned age test archive could not be downloaded.' }
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ine 'f48d8f8f9ebe903ab5027ed067652f2cc1db94bc206976430133b905dcd8e8c7') { throw 'Pinned test archive checksum mismatch.' }
    # Windows PowerShell 5.1 Expand-Archive treats brackets in DestinationPath as
    # wildcards; the framework API uses the literal path, matching our launcher.
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory($archive, $temp)
    $age = Join-Path $temp 'age\age.exe'
    if ((Get-FileHash -LiteralPath $age -Algorithm SHA256).Hash -ine '2821a4ed191da07372acd302e5f6feae7a7985e285e1417765ebe74025af45f0') { throw 'age test executable checksum mismatch.' }
    $keygen = Join-Path $temp 'age\age-keygen.exe'
    $identity = Join-Path $temp 'synthetic-identity.txt'
    Invoke-Native $keygen @('-o', $identity) | Out-Null
    $recipient = (Invoke-Native $keygen @('-y', $identity)).Trim()
    if ($recipient -notmatch '^age1[a-z0-9]{58}$') { throw 'Invalid synthetic recipient.' }

    $ssidText = 'Caf' + [char]0x00e9 + ' Test Network'
    $passwordText = 'SYNTHETIC-password-for-tests-only'
    $ssid = ConvertTo-SecureString $ssidText -AsPlainText -Force
    $password = ConvertTo-SecureString $passwordText -AsPlainText -Force
    $nonce = '0123456789abcdef0123456789abcdef'
    $fingerprint = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
    $capsule = Join-Path $temp 'synthetic-capsule.age'
    [LawUsb.Capsule]::Export($age, $recipient, $nonce, $fingerprint, $capsule, $ssid, $password, $false)
    $plain = Invoke-Native $age @('--decrypt', '-i', $identity, $capsule) | ConvertFrom-Json
    if ($plain.ssid -cne $ssidText -or $plain.password -cne $passwordText -or $plain.nonce -cne $nonce -or $plain.fingerprint -cne $fingerprint) { throw 'Windows credential round trip changed synthetic data.' }
    $before = (Get-FileHash -LiteralPath $capsule -Algorithm SHA256).Hash
    $refused = $false
    try { [LawUsb.Capsule]::Export($age, $recipient, $nonce, $fingerprint, $capsule, $ssid, $password, $false) }
    catch { $refused = $true }
    if (-not $refused -or (Get-FileHash -LiteralPath $capsule -Algorithm SHA256).Hash -cne $before) { throw 'Existing ciphertext was overwritten.' }
    & (Join-Path $PSScriptRoot 'windows-staging.ps1') -AgePath $age
    & (Join-Path $PSScriptRoot 'windows-menu.ps1') -AgePath $age
    Write-Host 'PASS: native Windows C# compilation, UTF-8 synthetic credential encryption/decryption, existing-file preservation.'
} finally {
    if ($ssid) { $ssid.Dispose() }
    if ($password) { $password.Dispose() }
    if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp -Recurse -Force }
}
