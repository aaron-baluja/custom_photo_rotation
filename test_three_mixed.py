#!/usr/bin/env python3
"""
Quick test script to verify the Three Mixed Photos layout is working
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from layout_manager import LayoutManager

def test_three_mixed_layout():
    """Test the Three Mixed Photos layout"""
    print("Testing Three Mixed Photos Layout")
    print("=" * 50)
    
    # Create layout manager for 2560x1440 (2K resolution)
    layout_manager = LayoutManager(2560, 1440)
    
    # Get available layouts
    available_layouts = layout_manager.get_available_layout_names()
    print(f"Available layouts: {available_layouts}")
    print(f"Total layouts: {layout_manager.get_layout_count()}\n")
    
    # Try to get the Three Mixed Photos layout
    if "Three Mixed Photos" in available_layouts:
        print("✓ Three Mixed Photos layout found!")
        
        # Set it as current
        if layout_manager.set_current_layout("Three Mixed Photos"):
            layout = layout_manager.get_current_layout()
            print(f"\n📋 Layout Details:")
            print(f"  Name: {layout.name}")
            print(f"  Type: {layout.type.value}")
            print(f"  Total dimensions: {layout.total_width}x{layout.total_height}")
            print(f"  Display duration: {layout.display_duration}ms ({layout.display_duration/1000}s)")
            print(f"  Number of panes: {len(layout.panes)}\n")
            
            # Show pane details
            for i, pane in enumerate(layout.panes, 1):
                print(f"  🖼️  Pane {i}: {pane.name.upper()}")
                print(f"     Position: ({pane.x}, {pane.y})")
                print(f"     Size: {pane.width}x{pane.height}")
                print(f"     Categories: {', '.join(pane.photo_categories)}")
                print()
            
            print("✓ Three Mixed Photos layout is properly configured!")
            return True
        else:
            print("✗ Failed to set Three Mixed Photos layout")
            return False
    else:
        print("✗ Three Mixed Photos layout NOT found!")
        return False

if __name__ == "__main__":
    success = test_three_mixed_layout()
    sys.exit(0 if success else 1)
