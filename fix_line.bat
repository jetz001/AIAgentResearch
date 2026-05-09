@echo off
echo ===================================================
echo   LINE PC Network Fix Tool (Run as Administrator)
echo ===================================================
echo.
echo [*] Changing DNS to Google DNS (8.8.8.8, 8.8.4.4)...
netsh interface ip set dns name="Ethernet" source=static address=8.8.8.8
netsh interface ip add dns name="Ethernet" addr=8.8.4.4 index=2
echo.
echo [*] Flushing DNS cache...
ipconfig /flushdns
echo.
echo [*] Resetting Winsock and IP stack...
netsh winsock reset
netsh int ip reset
echo.
echo ===================================================
echo   Done! Please RESTART your computer and try LINE.
echo ===================================================
pause
