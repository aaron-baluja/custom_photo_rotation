#!/usr/bin/env python3
"""
Build script to create a standalone executable using PyInstaller.
This script will package the entire application into a single .exe file.
"""

import os
import sys
import subprocess
import shutil

def build_executable():
    """Build the standalone executable using PyInstaller"""
    
    print("🔨 Building standalone executable...")
    
    # Clean up previous builds
    if os.path.exists("build"):
        print("🧹 Cleaning up previous build directory...")
        shutil.rmtree("build")
    
    if os.path.exists("dist"):
        print("🧹 Cleaning up previous dist directory...")
        shutil.rmtree("dist")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (for screen saver)
        "--name=PhotoRotationScreensaver",  # Executable name
        "--add-data=config.txt;.",      # Include config file
        "--add-data=requirements.txt;.", # Include requirements
        "--add-data=README.md;.",       # Include README
        "--icon=NONE",                  # No icon for now
        "--clean",                      # Clean cache
        "main.py"                       # Main script
    ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Check if executable was created
        exe_path = os.path.join("dist", "PhotoRotationScreensaver.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 File size: {file_size:.1f} MB")
            
            # Create a simple batch file for easy launching
            batch_path = os.path.join("dist", "Run_Screensaver.bat")
            with open(batch_path, "w") as f:
                f.write("@echo off\n")
                f.write("echo Starting Photo Rotation Screensaver...\n")
                f.write("PhotoRotationScreensaver.exe\n")
                f.write("pause\n")
            
            print(f"📝 Batch file created: {batch_path}")
            
            # Copy config file to dist if it exists
            if os.path.exists("config.txt"):
                shutil.copy2("config.txt", "dist/")
                print("📋 Config file copied to dist directory")
            
            print("\n🎉 Build complete! Files in 'dist' directory:")
            print("  - PhotoRotationScreensaver.exe (main executable)")
            print("  - Run_Screensaver.bat (easy launcher)")
            print("  - config.txt (configuration file)")
            print("\n💡 To distribute: Copy the entire 'dist' folder to users")
            
        else:
            print("❌ Executable not found after build!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error code {e.returncode}")
        print(f"📤 stdout: {e.stdout}")
        print(f"📥 stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during build: {e}")
        return False
    
    return True

def create_installer_script():
    """Create a simple installer script for end users"""
    
    installer_content = """@echo off
echo ========================================
echo Photo Rotation Screensaver Installer
echo ========================================
echo.
echo This will install the Photo Rotation Screensaver
echo to your desktop for easy access.
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Photo Rotation Screensaver.lnk'); $Shortcut.TargetPath = '%~dp0PhotoRotationScreensaver.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo ✅ Desktop shortcut created successfully!
    echo.
    echo 🎉 Installation complete!
    echo.
    echo You can now:
    echo   - Double-click the desktop shortcut to run
    echo   - Use Run_Screensaver.bat in this folder
    echo   - Edit config.txt to change image folder
    echo.
    echo Press any key to exit...
) else (
    echo ❌ Failed to create desktop shortcut
    echo You can still run the screensaver directly from this folder
    echo.
    echo Press any key to exit...
)

pause > nul
"""
    
    installer_path = os.path.join("dist", "Install.bat")
    with open(installer_path, "w") as f:
        f.write(installer_content)
    
    print(f"📦 Installer script created: {installer_path}")

if __name__ == "__main__":
    print("🚀 Photo Rotation Screensaver - Build Script")
    print("=" * 50)
    
    if build_executable():
        create_installer_script()
        print("\n🎯 Build and packaging complete!")
        print("📁 Check the 'dist' directory for your executable")
    else:
        print("\n💥 Build failed! Check the error messages above")
        sys.exit(1)

