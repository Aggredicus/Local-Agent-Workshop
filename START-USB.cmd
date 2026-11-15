@echo off
setlocal
powershell.exe -NoProfile -File "%~dp0setup\usb\Prepare-USB.ps1"
if errorlevel 1 (
  echo.
  echo USB setup did not complete. No execution-policy changes were made.
  echo Read setup\usb\README.md for trusted ZIP verification and PowerShell guidance.
  pause
)
