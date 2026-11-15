#Requires -Version 5.1
# Call the real checksum verifier with synthetic bytes; no network/disk device.
param()
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $repo 'setup\usb\Prepare-USB.ps1'),[ref]$tokens,[ref]$errors)
if ($errors.Count) {throw 'Preparation script does not parse.'}
$definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Confirm-ISO'},$false)
if (-not $definition) {throw 'ISO verifier missing.'}
. ([ScriptBlock]::Create($definition.Extent.Text))
$isoName='LAW-Debian-13.7.0-amd64.iso'
$temp=Join-Path ([IO.Path]::GetTempPath()) ("LAW ISO O'Brien [test] "+[guid]::NewGuid().ToString('N'))
try {
    [IO.Directory]::CreateDirectory($temp) | Out-Null
    $file=Join-Path $temp $isoName
    [IO.File]::WriteAllText($file,'Synthetic ISO bytes, never booted.')
    $hash=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
    [IO.File]::WriteAllText(($file+'.sha256'),($hash+'  '+$isoName+"`n"))
    if ((Confirm-ISO $file) -cne $hash) {throw 'Matching ISO rejected.'}
    [IO.File]::AppendAllText($file,'changed')
    $refused=$false
    try {Confirm-ISO $file | Out-Null} catch {$refused=$true}
    if (-not $refused) {throw 'Changed ISO accepted.'}
    [IO.File]::WriteAllText(($file+'.sha256'),('0'*64+'  different.iso'))
    $refused=$false
    try {Confirm-ISO $file | Out-Null} catch {$refused=$true}
    if (-not $refused) {throw 'Wrong checksum filename accepted.'}
    Remove-Item -LiteralPath ($file+'.sha256')
    $refused=$false
    try {Confirm-ISO $file | Out-Null} catch {$refused=$true}
    if (-not $refused) {throw 'Missing checksum accepted.'}
    Write-Host 'PASS: real ISO verifier accepts matching bytes and rejects tampering, wrong names and missing checksums.'
} finally {
    if (Test-Path -LiteralPath $temp) {Remove-Item -LiteralPath $temp -Recurse -Force}
}
