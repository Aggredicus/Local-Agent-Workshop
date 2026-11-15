#Requires -Version 5.1
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'

# START-USB.cmd obtains consent and starts this same process with RemoteSigned.
# Resolve literal paths relative to this file, including spaces, brackets and quotes.
$scripts = @('Prepare-USB.ps1', 'Wifi-Capsule.ps1') | ForEach-Object {
    $path = Join-Path $PSScriptRoot $_
    $file = Get-Item -LiteralPath $path -Force
    if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw 'Linked or invalid USB script rejected.'
    }
    $path
}
# Only these two files are unblocked; unrelated extracted scripts are untouched.
foreach ($path in $scripts) { Unblock-File -LiteralPath $path }
& (Join-Path $PSScriptRoot 'Prepare-USB.ps1')
