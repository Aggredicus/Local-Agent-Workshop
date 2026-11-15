@echo off
setlocal DisableDelayedExpansion
echo Run only after verifying the ZIP checksum and trusting these tools.
echo This unblocks the three included PowerShell scripts. Their unblock persists.
echo RemoteSigned applies only to the new PowerShell process; saved policies stay unchanged.
"%SystemRoot%\System32\choice.exe" /C YN /N /M "Start USB tools? [Y/N]: "
if errorlevel 255 goto approval_failed
if errorlevel 2 exit /b 0
if not errorlevel 1 goto approval_failed
set "LAW_USB_ROOT=%~dp0"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -Command "$ErrorActionPreference = 'Stop'; try { if ((Get-ExecutionPolicy) -notin @('RemoteSigned', 'Unrestricted')) { throw 'An enforced policy prevents this launcher. Ask your administrator about approved scripts.' }; $script = Join-Path $env:LAW_USB_ROOT 'setup\usb\Start-USB.ps1'; $file = Get-Item -LiteralPath $script -Force; if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Linked or invalid launcher rejected.' }; Unblock-File -LiteralPath $script; & $script } catch { Write-Host ('USB startup stopped: ' + $_.Exception.Message); exit 1 }"
set "LAW_USB_EXIT=%ERRORLEVEL%"
if not "%LAW_USB_EXIT%"=="0" (
  echo.
  echo USB setup did not complete. Saved execution policies were not changed.
  echo Read setup\usb\README.md for guidance. Administrator policies still apply.
  pause
)
exit /b %LAW_USB_EXIT%

:approval_failed
echo Approval could not be read. USB tools were not started.
pause
exit /b 1
