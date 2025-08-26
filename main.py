#!/usr/bin/env python3
"""
Main entry point for the Custom Photo Rotation Screen Saver.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from screensaver import ScreenSaver
from config_manager import ConfigManager
from logger import log_startup, log_shutdown, close_logger


def main():
    """Main application entry point"""
    try:
        print("🚀 Photo Rotation Screensaver starting...")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Executable location: {os.path.abspath(__file__)}")
        
        # Initialize logging system
        log_startup()
        
        # Show debug overlay controls
        print("🔍 Debug overlay controls:")
        print("   - Press 'v' to toggle debug overlay visibility")
        print("   - Press 'Enter' to manually advance to the next layout")
        print("   - Press 'Left Control' to start issue reporting (timer pauses)")
        print("   - Press 'Left Control' again to finish issue reporting (timer resumes)")
        print("   - Press 'Escape' or click to exit")
        print()
        
        print("📋 Loading configuration...")
        config = ConfigManager()
        print(f"✅ Configuration loaded successfully")
        print(f"   Image folder: {config.get('IMAGE_FOLDER', 'NOT SET')}")
        print(f"   Change interval: {config.get('CHANGE_INTERVAL', 'NOT SET')}")
        print(f"   Layout type: {config.get('LAYOUT_TYPE', 'NOT SET')}")
        print()
        
        print("🖼️ Starting screensaver application...")
        app = ScreenSaver()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
    finally:
        # Ensure logging is properly closed
        log_shutdown()
        close_logger()


if __name__ == "__main__":
    main()
