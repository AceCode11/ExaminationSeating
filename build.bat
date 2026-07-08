@echo off
REM ============================================================
REM  Build Script for Exam Automation System
REM  Creates a distributable .exe using PyInstaller
REM ============================================================

echo.
echo ====================================
echo   Exam Automation - Build Script
echo ====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

REM Install project dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM Clean previous build artifacts
echo [2/3] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the application
echo [3/3] Building application...
python -m PyInstaller ExamAutomation.spec --clean
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo ====================================
echo   BUILD SUCCESSFUL!
echo ====================================
echo.
echo Output location: dist\ExamAutomation\
echo Executable:      dist\ExamAutomation\ExamAutomation.exe
echo.
echo You can distribute the entire "dist\ExamAutomation" folder.
echo Users just need to run ExamAutomation.exe inside it.
echo.
pause
