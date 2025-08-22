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
        
        # Show debug overlay controls
        config = ConfigManager()
        print("🔍 Debug overlay controls:")
        print("   - Press 'v' to toggle debug overlay visibility")
        print("   - Press 'Enter' to manually advance to the next layout")
        print("   - Press 'Escape' or click to exit")
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
