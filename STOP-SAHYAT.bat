@echo off
echo Stopping Sahyat processes...
taskkill /FI "WINDOWTITLE eq Sahyat Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Sahyat Frontend*" /T /F >nul 2>&1
echo SAHYAT STOPPED
pause
