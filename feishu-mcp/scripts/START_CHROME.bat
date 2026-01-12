@echo off
echo ================================================
echo Starting Chrome with Remote Debugging
echo ================================================
echo.

REM Kill existing Chrome
echo Closing all Chrome windows...
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo.
echo Starting Chrome with remote debugging on port 9222...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 https://qcn9ppuir8al.feishu.cn/next/messenger/

echo.
echo ================================================
echo Chrome is starting...
echo.
echo Wait 10 seconds for it to fully load, then:
echo   1. Log into Feishu if needed
echo   2. Run: python feishu_cdp.py test
echo.
echo Keep Chrome open for automation to work!
echo ================================================
echo.
pause
