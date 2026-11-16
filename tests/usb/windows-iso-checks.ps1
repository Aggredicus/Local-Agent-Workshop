#Requires -Version 5.1
# Call the real checksum verifier with synthetic bytes; no network/disk device.
param()
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$tokens=$null; $errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $repo 'setup\usb\Prepare-USB.ps1'),[ref]$tokens,[ref]$errors)
if ($errors.Count) {throw 'Preparation script does not parse.'}
foreach ($name in @('Convert-DataPath','Test-DataLink','Resolve-ISOPath','Confirm-ISO','Select-ISOPath','Get-LawISO')) {
    $definition=$ast.Find({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq $name},$false)
    if (-not $definition) {throw ('ISO helper missing: '+$name)}
    . ([ScriptBlock]::Create($definition.Extent.Text))
}
$isoName='LAW-Debian-13.7.0-amd64.iso'
$temp=Join-Path ([IO.Path]::GetTempPath()) ("LAW ISO O'Brien [test] "+[guid]::NewGuid().ToString('N'))
try {
    [IO.Directory]::CreateDirectory($temp) | Out-Null
    $file=Join-Path $temp $isoName
    $original='Synthetic ISO bytes, never booted.'
    [IO.File]::WriteAllText($file,$original)
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
    # Test the fallback trust input with a synthetic digest, not real credentials.
    [IO.File]::WriteAllText($file,$original)
    $publishedISOHash=$hash
    if ((Confirm-ISO $file) -cne $hash) {throw 'Pinned fallback rejected authenticated bytes without a sidecar.'}
    if ((Resolve-ISOPath ('"'+$file+'"')) -cne $file) {throw 'Copy-as-path quotes were not removed.'}
    if ((Resolve-ISOPath ('"'+$temp+'"')) -cne $file) {throw 'Containing folder was not resolved to the ISO.'}
    if ((Resolve-ISOPath ("'"+$temp+"'")) -cne $file) {throw 'Single-quoted folder was not resolved.'}
    $cloud=[pscustomobject]@{Attributes=[IO.FileAttributes]::ReparsePoint; LinkType=$null}
    if (Test-DataLink $cloud) {throw 'Cloud placeholder metadata was mistaken for a symbolic link.'}
    $link=[pscustomobject]@{Attributes=[IO.FileAttributes]::ReparsePoint; LinkType='Junction'}
    if (-not (Test-DataLink $link)) {throw 'Junction metadata was accepted.'}
    $desktopISO=Join-Path $temp ('wrong-location/'+$isoName)
    $script:lastISOPath=$desktopISO
    $script:isoAnswer='"'+$temp+'"'
    function Read-Host([string]$Prompt) {return $script:isoAnswer}
    function Invoke-RestMethod {throw 'Existing-ISO verification must not call the network.'}
    Get-LawISO
    if ($script:lastISOPath -cne $file) {throw 'Verified download location was not remembered.'}
    $script:isoAnswer=''
    if ((Select-ISOPath) -cne $file) {throw 'Option 3 did not default to the remembered custom location.'}
    [IO.File]::AppendAllText($file,'changed again')
    $refused=$false
    try {Confirm-ISO $file | Out-Null} catch {$refused=$true}
    if (-not $refused) {throw 'Pinned fallback accepted changed bytes.'}
    $missing=Join-Path $temp 'missing.iso'
    $message=''
    try {Confirm-ISO $missing | Out-Null} catch {$message=$_.Exception.Message}
    if (-not $message.Contains('ISO file not found:')) {throw 'Missing ISO error was not specific.'}
    Write-Host 'PASS: ISO checks, quotes/folders, cloud data classification, pinned fallback, tampering rejection, existing-file reuse, and remembered option-3 location.'
} finally {
    if (Test-Path -LiteralPath $temp) {Remove-Item -LiteralPath $temp -Recurse -Force}
}
