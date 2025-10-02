#!/bin/bash

# YouTube Downloader Pro - Quick Start Script
echo "========================================"
echo "  YouTube Downloader Pro - Quick Start"
echo "========================================"
echo

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if python is actually Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
    else
        echo "[ERROR] Found Python 2, but Python 3.7+ is required"
        echo "Please install Python 3.7+"
        echo "  macOS: brew install python"
        echo "  Ubuntu/Debian: sudo apt install python3"
        exit 1
    fi
else
    echo "[ERROR] Python is not installed"
    echo "Please install Python 3.7+"
    echo "  macOS: brew install python"
    echo "  Ubuntu/Debian: sudo apt install python3"
    exit 1
fi

echo "[INFO] Python found: $($PYTHON_CMD --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "[SETUP] Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[SUCCESS] Virtual environment created!"
fi

# Activate virtual environment
echo ""
echo "[SETUP] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "[SETUP] Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo ""
echo "[SETUP] Installing/updating requirements..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install requirements"
    echo "[INFO] Trying to install individual packages..."
    pip install "yt-dlp>=2023.12.30"
    pip install "ffmpeg-python>=0.2.0"
fi

# Check if FFmpeg is available
echo ""
echo "[CHECK] Checking FFmpeg availability..."
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARNING] FFmpeg not found in PATH"
    echo "[INFO] The app will try to auto-detect FFmpeg location"
    echo "If downloads fail, please install FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
else
    echo "[SUCCESS] FFmpeg found in PATH"
fi

# Run the application
echo ""
echo "========================================"
echo "  Starting YouTube Downloader Pro"
echo "========================================"
echo ""
python download.py

# Handle errors
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Application encountered an error"
    read -p "Press Enter to exit..."
fi