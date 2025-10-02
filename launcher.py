#!/usr/bin/env python3
"""
Universal Cross-Platform Launcher
=================================

Universal launcher for the YouTube Downloader application.
Automatically detects your operating system and runs the appropriate setup script.

Features:
- Cross-platform compatibility (Windows, macOS, Linux)
- Automatic platform detection
- Integrated setup and launch process
- Error handling and user feedback

"""

import os
import sys
import platform
import subprocess


# ====================================================================
# Platform Detection and Setup
# ====================================================================

def get_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unix"

def run_setup():
    """Run the appropriate setup script based on platform"""
    current_platform = get_platform()
    
    print(f"🖥️  Detected platform: {current_platform.title()}")
    print("🚀 Starting YouTube Downloader Pro setup...")
    print()
    
    try:
        if current_platform == "windows":
            # Use the unified RUN.bat file
            subprocess.run(["RUN.bat"], check=True, shell=True)
        else:
            # macOS/Linux - use RUN.sh
            if os.path.exists("RUN.sh"):
                # Make executable
                os.chmod("RUN.sh", 0o755)
                subprocess.run(["./RUN.sh"], check=True)
            else:
                print("❌ RUN.sh script not found!")
                sys.exit(1)
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed with error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_setup()