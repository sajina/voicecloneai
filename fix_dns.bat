@echo off
echo.
echo ===================================================
echo     FIXING DNS SETTINGS FOR RAILWAY ACCESS
echo ===================================================
echo.
echo Current Status: Your local DNS server (10.218.148.85) is BLOCKING
echo                Railway domains. We need to switch to Google DNS (8.8.8.8).
echo.
echo 1. Requesting Admin Privileges...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo    - Admin privileges confirmed.
) else (
    echo    - FAILURE: Please right-click this script and "Run as Administrator"
    pause
    exit
)
echo.

echo 2. Setting "Wi-Fi" DNS to Google (8.8.8.8 / 8.8.4.4)...
netsh interface ip set dns name="Wi-Fi" static 8.8.8.8 primary
if %errorLevel% == 0 (
    echo    - Primary DNS set to 8.8.8.8 [OK]
) else (
    echo    - ERROR: Could not set primary DNS.
)

netsh interface ip add dns name="Wi-Fi" 8.8.4.4 index=2
if %errorLevel% == 0 (
    echo    - Secondary DNS set to 8.8.4.4 [OK]
) else (
    echo    - ERROR: Could not set secondary DNS (might already be set).
)
echo.

echo 3. Flushing DNS Cache...
ipconfig /flushdns
echo.

echo 4. Testing Connection to Railway...
nslookup voicecloneai-production-9820.up.railway.app 8.8.8.8
echo.
echo.
echo ===================================================
echo     FIX COMPLETE - PLEASE TRY ACCESSING THE SITE
echo ===================================================
echo.
pause
