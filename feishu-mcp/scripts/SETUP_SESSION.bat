@echo off
echo ================================================
echo FEISHU SESSION SETUP
echo ================================================
echo.
echo This is a ONE-TIME setup.
echo.
echo What will happen:
echo 1. Chrome will open to Feishu
echo 2. You log in normally (just once!)
echo 3. Your session is saved forever
echo 4. Future commands work automatically
echo.
echo After this, you'll NEVER log in again!
echo ================================================
echo.
pause

python feishu_persistent.py setup

echo.
echo ================================================
echo Setup complete!
echo.
echo Now you can use:
echo   python feishu_persistent.py send Hany "message"
echo   python feishu_persistent.py read Hany
echo   python feishu_persistent.py list
echo.
echo No more logins needed!
echo ================================================
pause
