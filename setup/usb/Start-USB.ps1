#Requires -Version 5.1
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

# START-USB.cmd obtains consent and starts this same process with RemoteSigned.
# Resolve literal paths relative to this file, including spaces, brackets and quotes.
$scripts = @('Prepare-USB.ps1', 'Wifi-Capsule.ps1')
foreach ($name in $scripts) {
    $path = Join-Path $PSScriptRoot $name
    $file = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw 'Linked or invalid USB script rejected.'
    }
}
# Only these two files are unblocked; unrelated extracted scripts are untouched.
foreach ($name in $scripts) { Unblock-File -LiteralPath (Join-Path $PSScriptRoot $name) }
& (Join-Path $PSScriptRoot 'Prepare-USB.ps1')
