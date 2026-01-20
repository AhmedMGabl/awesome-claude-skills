@echo off
echo ========================================
echo Feishu Bot API Setup
echo ========================================
echo.

REM Set environment variables
set FEISHU_APP_ID=cli_a85833b3fc39900e
set FEISHU_APP_SECRET=fiFRoqlAFX7ASY9iUt7Evb2aUx6Qurkd

echo [OK] Credentials set for this session!
echo.
echo App ID: %FEISHU_APP_ID%
echo App Secret: %FEISHU_APP_SECRET%
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Add your bot "AA" to the chat with Hany:
echo    - Open Feishu
echo    - Go to chat with Hany
echo    - Click "..." menu
echo    - Select "Add Bot"
echo    - Search for "AA"
echo    - Add to chat
echo.
echo 2. Get chat ID:
echo    python scripts\feishu_bot.py list
echo.
echo 3. Send a test message:
echo    python scripts\feishu_bot.py send CHAT_ID "Hello from Bot API!"
echo.
echo ========================================
echo.

REM Keep window open
cmd /k
