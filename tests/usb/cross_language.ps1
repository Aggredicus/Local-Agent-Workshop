param([string]$RequestFile, [string]$AgePath, [string]$CapsulePath, [string]$Repo)
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Repo 'setup/usb/Wifi-Capsule.cs')
$pair = Get-Content -LiteralPath $RequestFile -Raw | ConvertFrom-Json
# Public synthetic test data only; never used as a real network credential.
$ssid = ConvertTo-SecureString 'Café Test Network' -AsPlainText -Force
$password = ConvertTo-SecureString 'SYNTHETIC-password-for-tests-only' -AsPlainText -Force
try { [LawUsb.Capsule]::Export($AgePath, $pair.recipient, $pair.nonce, $pair.fingerprint, $CapsulePath, $ssid, $password, $false) }
finally { $ssid.Dispose(); $password.Dispose() }
Write-Host 'CROSS_LANGUAGE_ENCRYPTION_PASSED'
