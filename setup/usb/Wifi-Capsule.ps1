#Requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Request,
    [string]$OutputDirectory,
    [string]$AgePath = (Join-Path $PSScriptRoot 'tools\age.exe'),
    [switch]$CompileOnly
)
$ErrorActionPreference = 'Stop'
try {
    # No credential-bearing PowerShell function parameters or command-line arguments.
    if ($PSVersionTable.PSVersion.Major -ge 6) { Add-Type -Path (Join-Path $PSScriptRoot 'Wifi-Capsule.cs') }
    else { Add-Type -Path (Join-Path $PSScriptRoot 'Wifi-Capsule.cs') -ReferencedAssemblies @('System.dll', 'System.Core.dll', 'System.Runtime.Serialization.dll', 'System.Xml.dll') }
    if ($CompileOnly) { Write-Host 'C# helper compiled. Native Windows Wi-Fi was not tested.'; exit 0 }
    $trustedRoot = Join-Path $env:LOCALAPPDATA 'LocalAgentWorkshop\USBTools\setup\usb'
    if ([IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\') -ine [IO.Path]::GetFullPath($trustedRoot).TrimEnd('\')) { throw 'Run the locally staged Windows tools, not scripts on the returning USB.' }
    if (-not $Request) { $Request = Read-Host 'Path to the PUBLIC Debian pairing request JSON' }
    $pair = Get-Content -LiteralPath $Request -Raw | ConvertFrom-Json
    if ($pair.schema -ne 1 -or $pair.recipient -notmatch '^age1[a-z0-9]{58}$' -or $pair.nonce -notmatch '^[a-f0-9]{32}$') { throw 'Invalid public pairing request.' }
    $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    if ([long]$pair.expires -le $now -or [long]$pair.expires -gt ($now + 87000)) { throw 'Pairing request expired or has an invalid lifetime.' }
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $fingerprint = ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($pair.recipient)))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
    Write-Host ('Debian device: ' + ([regex]::Replace([string]$pair.hostname, '[^a-zA-Z0-9.-]', '?')))
    Write-Host ('Public-key fingerprint: ' + $fingerprint)
    $expected = Read-Host 'Enter the full fingerprint displayed at the Debian console (public information)'
    if ($expected -cne $fingerprint) { throw 'Fingerprint mismatch; no credentials requested.' }
    if (-not (Test-Path -LiteralPath $AgePath -PathType Leaf)) { throw 'Verified age.exe is missing. Use the Windows tools preparation step.' }
    if ((Get-FileHash -LiteralPath $AgePath -Algorithm SHA256).Hash -ine '2821a4ed191da07372acd302e5f6feae7a7985e285e1417765ebe74025af45f0') { throw 'age.exe integrity check failed; no credentials requested.' }
    if (-not $OutputDirectory) { $OutputDirectory = Read-Host 'Output folder for ENCRYPTED files on the USB' }
    $folder = (Resolve-Path -LiteralPath $OutputDirectory).ProviderPath
    $output = Join-Path $folder ('wifi-' + $pair.nonce + '.age')
    if (Test-Path -LiteralPath $output) { throw 'Output already exists. Preserve it and use another folder.' }
    $test = (Read-Host 'Test using the Windows Wi-Fi adapter? This may interrupt Wi-Fi temporarily. Type TEST or press Enter to skip') -ceq 'TEST'
    $ssid = Read-Host 'Wi-Fi network name (hidden)' -AsSecureString
    $password = Read-Host 'Wi-Fi password (hidden; never paste it into chat)' -AsSecureString
    try { [LawUsb.Capsule]::Export((Resolve-Path -LiteralPath $AgePath).ProviderPath, $pair.recipient, $pair.nonce, $fingerprint, $output, $ssid, $password, $test) }
    finally { $ssid.Dispose(); $password.Dispose() }
    Write-Host 'Encrypted Wi-Fi file created. Only Debian holding the paired private key can decrypt it.'
    if ($test) { Write-Host 'Windows temporary-profile authentication confirmed; Debian hardware must still be tested.' }
    else { Write-Host 'Credentials were NOT tested on Windows. Debian will test association before keeping configuration.' }
    Write-Host ('Return this file to Debian: ' + $output)
    Write-Host ('Ciphertext SHA256 (compare at Debian console): ' + (Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash.ToLowerInvariant())
} catch {
    # CompileOnly exits before any credential input, so compiler diagnostics are safe.
    if ($CompileOnly) { throw }
    # Error text is deliberately generic: do not serialize exception objects/credential-bearing locals.
    Write-Error 'Wi-Fi export did not complete. Check the public pairing fingerprint, verified age tool, supported WPA2 input, adapter availability and USB path. No plaintext diagnostic bundle was written.'
    exit 1
}
