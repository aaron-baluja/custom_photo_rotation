#!/usr/bin/env python3
"""
Comprehensive build script for Photo Rotation Screensaver distribution.
This script creates a complete standalone executable package.
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def print_header():
    """Print build header"""
    print("=" * 60)
    print("🚀 PHOTO ROTATION SCREENSAVER - DISTRIBUTION BUILDER")
    print("=" * 60)
    print(f"📅 Build started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def clean_build_directories():
    """Clean up previous build artifacts"""
    print("🧹 Cleaning up previous builds...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✅ Cleaned {dir_name}")
    
    # Clean .spec files
    spec_files = [f for f in os.listdir(".") if f.endswith(".spec")]
    for spec_file in spec_files:
        os.remove(spec_file)
        print(f"   ✅ Cleaned {spec_file}")
    
    print()

def check_requirements():
    """Check if required files exist"""
    print("🔍 Checking requirements...")
    
    required_files = [
        "main.py",
        "config.txt", 
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"   ✅ {file_name}")
        else:
            missing_files.append(file_name)
            print(f"   ❌ {file_name} (MISSING)")
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print()
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable with PyInstaller...")
    
    cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (production mode)
        "--name=PhotoRotationScreensaver",  # Executable name
        "--add-data=src;src",           # Include entire src directory
        "--add-data=config.txt;.",      # Include config file
        "--add-data=requirements.txt;.", # Include requirements
        "--add-data=README.md;.",       # Include README
        "--hidden-import=screensaver",  # Explicitly include screensaver module
        "--hidden-import=config_manager", # Explicitly include config_manager module
        "--hidden-import=photo_classifier", # Explicitly include photo_classifier module
        "--hidden-import=photo_metadata", # Explicitly include photo_metadata module
        "--hidden-import=layout_manager", # Explicitly include layout_manager module
        "--hidden-import=photo_selector", # Explicitly include photo_selector module
        "--hidden-import=utils",        # Explicitly include utils module
        "--hidden-import=logger",       # Explicitly include logger module
        "--hidden-import=tkinter",      # Explicitly include tkinter
        "--hidden-import=tkinter.ttk",  # Explicitly include tkinter.ttk
        "--hidden-import=tkinter.messagebox", # Explicitly include tkinter.messagebox
        "--hidden-import=PIL",          # Explicitly include PIL
        "--hidden-import=PIL.Image",    # Explicitly include PIL.Image
        "--hidden-import=PIL.ImageTk",  # Explicitly include PIL.ImageTk
        "--hidden-import=PIL._tkinter_finder",  # Ensure PIL is properly included
        "--collect-all=PIL",            # Collect all PIL modules
        "--collect-all=tkinter",        # Collect all tkinter modules
        "--clean",                      # Clean cache
        "main.py"                       # Main script
    ]
    
    print(f"   Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ PyInstaller build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ PyInstaller build failed!")
        print(f"   📤 stdout: {e.stdout}")
        print(f"   📥 stderr: {e.stderr}")
        return False

def create_helper_files():
    """Create helper batch files and documentation"""
    print("📝 Creating helper files...")
    
    # Copy source files (but not config.txt since we'll create a template version)
    # Removed requirements.txt and README.md from distribution
    files_to_copy = []
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, "dist/")
            print(f"   ✅ Copied {file_name}")
    
    # Create template config file (this will be the config.txt users edit)
    create_template_config()
    
    # Create Run_Screensaver.bat
    run_bat_content = """@echo off
echo ========================================
echo Photo Rotation Screensaver
echo ========================================
echo.
echo Starting Photo Rotation Screensaver...
echo.
echo Controls:
echo   - Press 'v' to toggle debug overlay
echo   - Press 'Enter' to advance to next layout
echo   - Press 'Left Control' for issue reporting
echo   - Press 'Escape' or click to exit
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul
echo.
echo Launching screensaver...
PhotoRotationScreensaver.exe
echo.
echo Screensaver closed.
pause
"""
    
    with open("dist/Run_Screensaver.bat", "w") as f:
        f.write(run_bat_content)
    print("   ✅ Created Run_Screensaver.bat")
    
    print()

def create_template_config():
    """Create a template config file with all available options"""
    template_config_content = """# ========================================
# PHOTO ROTATION SCREENSAVER - CONFIG TEMPLATE
# ========================================
# 
# This is a template configuration file. Edit the values below to match
# your setup. The screensaver will look for this file in the same folder
# as the executable.
#
# IMPORTANT: Change IMAGE_FOLDER to point to your photo collection!
#
# ========================================
# REQUIRED SETTINGS
# ========================================

# Path to the folder containing your photos
# Use double backslashes (\\) or forward slashes (/) in the path
# Example: IMAGE_FOLDER=C:\\Users\\YourName\\Pictures\\Screensaver
# Example: IMAGE_FOLDER=C:/Users/YourName/Pictures/Screensaver
IMAGE_FOLDER=C:\\Path\\To\\Your\\Photos

# ========================================
# DISPLAY SETTINGS
# ========================================

# How often layouts and photos change (in milliseconds)
# 5000 = 5 seconds (very fast)
# 10000 = 10 seconds (fast)
# 15000 = 15 seconds (default)
# 30000 = 30 seconds (slow)
# 60000 = 1 minute (very slow)
CHANGE_INTERVAL=15000

# ========================================
# LAYOUT SETTINGS
# ========================================

# Available layout types:
# auto = automatically rotate through all available layouts (recommended)
# single_pane = always show one photo filling the screen
# dual_pane = always show two photos side by side
# triple_vertical = always show three vertical photos
LAYOUT_TYPE=auto

# ========================================
# ADVANCED SETTINGS
# ========================================

# Enable debug mode to show metadata overlays on photos
# true = show debug info, false = hide debug info
# You can also press 'v' key to toggle this while running
DEBUG_MODE=false

# ========================================
# NOTES
# ========================================
#
# - The screensaver automatically classifies photos by aspect ratio
# - Supports JPG, JPEG, and PNG files
# - Will search subfolders automatically
# - Photos are automatically cropped to fit layouts while preserving aspect ratios
# - Ultra-wide photos maintain their natural proportions
# - The program creates a 'logs' folder for troubleshooting
#
# ========================================
# CONTROLS (while screensaver is running)
# ========================================
#
# v = Toggle debug overlay visibility
# Enter = Manually advance to next layout
# Left Control = Start/finish issue reporting
# Escape = Exit screensaver
# Mouse click = Exit screensaver
#
# ========================================
"""
    
    with open("dist/config.txt", "w", encoding="utf-8") as f:
        f.write(template_config_content)
    print("   ✅ Created config.txt (template)")

def create_user_guide():
    """Create comprehensive user guide"""
    print("📖 Creating user documentation...")
    
    user_guide_content = """PHOTO ROTATION SCREENSAVER - USER GUIDE
==========================================

🎯 WHAT IS THIS?
This is a standalone executable that displays your photos as a screen saver
with automatic layout rotation. No Python installation required!

📁 FILES INCLUDED:
- PhotoRotationScreensaver.exe (main program)
- Run_Screensaver.bat (easy launcher)
- config.txt (configuration file - edit this for your photos)
- User_Guide.txt (this file)

🚀 GETTING STARTED:

1. FIRST TIME SETUP:
   - Run "PhotoRotationScreensaver.exe" directly
   - Or use "Run_Screensaver.bat" for easy launching

2. CONFIGURE YOUR PHOTOS:
   - Edit "config.txt" with a text editor
   - Change IMAGE_FOLDER to point to your photo collection
   - Example: IMAGE_FOLDER=C:\\Users\\YourName\\Pictures\\Screensaver
   - The file contains detailed comments for all options

3. RUN THE SCREENSAVER:
   - Double-click "PhotoRotationScreensaver.exe", OR
   - Double-click "Run_Screensaver.bat"

⌨️ CONTROLS:
- Press 'v' to toggle debug overlay (shows photo info)
- Press 'Enter' to manually advance to next layout
- Press 'Left Control' to start issue reporting
- Press 'Left Control' again to finish issue reporting
- Press 'Escape' or click to exit

⚙️ CONFIGURATION OPTIONS (in config.txt):

IMAGE_FOLDER=C:\\Path\\To\\Your\\Photos
- Set this to the folder containing your photos
- Supports JPG, JPEG, and PNG files
- Will search subfolders automatically

CHANGE_INTERVAL=15000
- How often layouts change (in milliseconds)
- 15000 = 15 seconds (default)
- 5000 = 5 seconds (faster)
- 30000 = 30 seconds (slower)

LAYOUT_TYPE=auto
- auto = automatically rotate through layouts
- single_pane = always single photo
- dual_pane = always two photos side by side
- triple_vertical = always three vertical photos

🖼️ SUPPORTED PHOTO FORMATS:
- JPG/JPEG
- PNG
- Photos are automatically classified by aspect ratio
- Supports 16:9, 4:3, 1:1 (square), and ultra-wide photos

🔧 TROUBLESHOOTING:

1. "No images found" error:
   - Check that IMAGE_FOLDER path is correct in config.txt
   - Ensure the folder contains JPG, JPEG, or PNG files
   - Try using forward slashes (/) instead of backslashes (\\)

2. Program won't start:
   - Make sure you're running on Windows 10/11
   - Try running as administrator
   - Check Windows Defender isn't blocking the file

3. Photos look distorted:
   - The program automatically crops photos to fit layouts
   - Ultra-wide photos maintain their aspect ratio
   - Use 'v' key to see debug info about photo display

4. Want to change photo rotation speed:
   - Edit CHANGE_INTERVAL in config.txt
   - Lower numbers = faster rotation
   - Higher numbers = slower rotation

📝 LOGGING:
- The program automatically creates a "logs" folder
- Each session gets a timestamped log file
- Useful for troubleshooting issues

🎨 LAYOUTS AVAILABLE:
- Single Pane: One photo fills the screen
- Dual Pane: Two photos side by side (requires 1920x1080+)
- Triple Vertical: Three vertical photos (requires 1920x1080+)

💡 TIPS:
- Use 'v' key to see detailed photo information
- Press Enter to manually advance if you want to skip a photo
- Use Left Control for issue reporting if you notice problems
- The program runs in fullscreen mode for authentic screen saver experience
- Check config.txt for detailed configuration options and examples

🔄 UPDATES:
To update the screensaver:
1. Download the new version
2. Replace the old files with new ones

📞 SUPPORT:
If you encounter issues:
1. Check this user guide first
2. Look at the log files in the "logs" folder
3. Use the debug overlay ('v' key) to see what's happening
4. Report issues using the Left Control key feature
5. Check config.txt for configuration help and examples

🎉 ENJOY YOUR PHOTO SCREENSAVER!
The program will automatically rotate through your photos and layouts,
creating a beautiful, ever-changing display of your memories.
"""
    
    with open("dist/User_Guide.txt", "w", encoding="utf-8") as f:
        f.write(user_guide_content)
    print("   ✅ Created User_Guide.txt")
    
    # Create distribution README
    dist_readme_content = f"""PHOTO ROTATION SCREENSAVER - DISTRIBUTION PACKAGE
==================================================

🎯 WHAT IS THIS?
This is a complete, standalone distribution package of the Photo Rotation Screensaver.
End users can run this without needing Python or any source code.

📁 PACKAGE CONTENTS:
- PhotoRotationScreensaver.exe - Main executable
- config.txt - Configuration file (edit to point to photo folder)
- Run_Screensaver.bat - Easy launcher script
- Install.bat - Creates desktop shortcut
- Test_Executable.bat - Tests if executable works
- User_Guide.txt - Comprehensive user guide
- README.md - Technical documentation
- requirements.txt - Dependencies list (for reference)

🚀 FOR END USERS:

1. EXTRACT ALL FILES to a folder (e.g., C:\\PhotoScreensaver)
2. Edit config.txt to set IMAGE_FOLDER to your photo collection
3. Double-click Install.bat to create desktop shortcut
4. Or run PhotoRotationScreensaver.exe directly

⚙️ SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- 8GB RAM recommended
- 100MB free disk space
- Screen resolution 1920x1080 or higher for multi-pane layouts

🔧 BUILDING FROM SOURCE:
If you need to rebuild this executable:

1. Install Python 3.7+ and pip
2. Install dependencies: pip install -r requirements.txt
3. Install PyInstaller: pip install pyinstaller
4. Run: python -m PyInstaller --onefile --windowed --name=PhotoRotationScreensaver --add-data="config.txt;." --add-data="requirements.txt;." --add-data="README.md;." --clean main.py

📦 DISTRIBUTION:
- Copy the entire dist folder to users
- Users can run from any location
- No installation required
- Self-contained executable

🔄 UPDATES:
To update the distribution:
1. Rebuild the executable using PyInstaller
2. Replace old files with new ones
3. Users can update by replacing their old files

📝 TECHNICAL NOTES:
- Built with PyInstaller
- Python 3.12.10
- Includes all dependencies (PIL, tkinter, etc.)
- No external DLLs required
- Windows Defender compatible

🎉 READY FOR DISTRIBUTION!
This package contains everything end users need to run the Photo Rotation Screensaver
without any technical knowledge or additional software installation.

📅 Built on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open("dist/DISTRIBUTION_README.txt", "w", encoding="utf-8") as f:
        f.write(dist_readme_content)
    print("   ✅ Created DISTRIBUTION_README.txt")
    
    print()

def verify_build():
    """Verify the build was successful"""
    print("🔍 Verifying build...")
    
    required_dist_files = [
        "PhotoRotationScreensaver.exe",
        "config.txt",  # Now created as template
        "Run_Screensaver.bat",
        "User_Guide.txt",
        "DISTRIBUTION_README.txt"
    ]
    
    missing_files = []
    for file_name in required_dist_files:
        if os.path.exists(os.path.join("dist", file_name)):
            file_size = os.path.getsize(os.path.join("dist", file_name))
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
            print(f"   ✅ {file_name} ({size_str})")
        else:
            missing_files.append(file_name)
            print(f"   ❌ {file_name} (MISSING)")
    
    if missing_files:
        print(f"\n❌ Build verification failed! Missing files: {', '.join(missing_files)}")
        return False
    
    # Check executable size
    exe_path = os.path.join("dist", "PhotoRotationScreensaver.exe")
    if os.path.exists(exe_path):
        exe_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"\n📦 Executable size: {exe_size:.1f} MB")
        
        if exe_size < 1:
            print("   ⚠️  Executable seems too small - build may have failed")
            return False
        elif exe_size > 100:
            print("   ⚠️  Executable seems too large - check for unnecessary dependencies")
    
    print("\n✅ Build verification passed!")
    return True

def print_summary():
    """Print build summary"""
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("📁 Distribution package created in 'dist' folder:")
    print()
    
    dist_files = os.listdir("dist")
    for file_name in sorted(dist_files):
        file_path = os.path.join("dist", file_name)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            if file_size > 1024*1024:
                size_str = f"{file_size / (1024*1024):.1f} MB"
            else:
                size_str = f"{file_size / 1024:.1f} KB"
            print(f"   📄 {file_name} ({size_str})")
    
    print()
    print("🚀 READY FOR DISTRIBUTION!")
    print()
    print("💡 To distribute to users:")
    print("   1. Zip the entire 'dist' folder")
    print("   2. Send the zip file to users")
    print("   3. Users extract and run PhotoRotationScreensaver.exe")
    print()
    print("🔧 To rebuild in the future:")
    print("   python build_distribution.py")
    print()
    print(f"📅 Build completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main build function"""
    try:
        print_header()
        
        if not check_requirements():
            print("❌ Build failed due to missing requirements!")
            sys.exit(1)
        
        clean_build_directories()
        
        if not build_executable():
            print("❌ Build failed during PyInstaller execution!")
            sys.exit(1)
        
        create_helper_files()
        create_user_guide()
        
        if not verify_build():
            print("❌ Build verification failed!")
            sys.exit(1)
        
        print_summary()
        
    except Exception as e:
        print(f"\n💥 Build failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

