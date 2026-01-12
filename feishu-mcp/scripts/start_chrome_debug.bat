@echo off
REM Start Chrome with Remote Debugging for Feishu Automation
REM This allows scripts to control your browser without opening new windows

echo ===============================================
echo Chrome Remote Debugging Launcher
echo ===============================================
echo.
echo This will:
echo 1. Close all Chrome windows
echo 2. Start Chrome with remote debugging on port 9222
echo 3. Allow automation scripts to use your session
echo.

REM Close all Chrome instances
echo Closing existing Chrome windows...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo Starting Chrome with remote debugging...
echo.

REM Start Chrome with remote debugging
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=9222 ^
    --user-data-dir="%USERPROFILE%\.chrome-debug-profile" ^
    "https://qcn9ppuir8al.feishu.cn/next/messenger/"

echo.
echo ===============================================
echo Chrome is now ready for automation!
echo ===============================================
echo.
echo Next steps:
echo 1. Log into Feishu if needed
echo 2. Keep this window open
echo 3. Run automation scripts:
echo    - python feishu_cdp.py send Hany "message"
echo    - python feishu_simple.py send Hany "message"
echo.
echo Press Ctrl+C to stop Chrome remote debugging
echo ===============================================

REM Keep window open
pause
