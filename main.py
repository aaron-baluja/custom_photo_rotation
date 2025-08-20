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


def main():
    """Main application entry point"""
    try:
        print("Starting Custom Photo Rotation Screen Saver...")
        
        # Check debug mode for appropriate instructions
        config = ConfigManager()
        if config.is_debug_mode_enabled():
            print("🔧 DEBUG MODE ENABLED")
            print("Press Enter to advance to next photo rotation")
            print("Press Escape or any other key to exit")
        else:
            print("Press Escape, any key, or click to exit")
        print()
        
        app = ScreenSaver()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
