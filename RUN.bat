@echo off
title YouTube Downloader Pro
color 0A

echo ========================================
echo  YouTube Downloader Pro - Quick Start
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if Python is version 3
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
if "%PYTHON_VERSION:~0,1%" NEQ "3" (
    echo [ERROR] Found Python 2, but Python 3.7+ is required
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python found: 
python --version

:: Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created!
)

:: Activate virtual environment
echo.
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo.
echo [SETUP] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

:: Install requirements
echo.
echo [SETUP] Installing/updating requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    echo [INFO] Trying to install individual packages...
    pip install yt-dlp>=2023.12.30
    pip install ffmpeg-python>=0.2.0
)

:: Check if FFmpeg is available
echo.
echo [CHECK] Checking FFmpeg availability...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not found in PATH
    echo [INFO] The app will try to auto-detect FFmpeg location
    echo [INFO] If downloads fail, please install FFmpeg from: https://ffmpeg.org/download.html
) else (
    echo [SUCCESS] FFmpeg found in PATH
)

:: Run the application
echo.
echo ========================================
echo  Starting YouTube Downloader Pro
echo ========================================
echo.
python download.py

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo [ERROR] Application encountered an error
    pause
)

pause