#!/usr/bin/env python3
"""
Demo script to show how the layout system works.
This script demonstrates the layout management without running the full screen saver.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from layout_manager import LayoutManager
from photo_selector import PhotoSelector
from photo_classifier import PhotoClassifier
from photo_metadata import PhotoMetadata
from config_manager import ConfigManager


def demo_layout_system():
    """Demonstrate the layout system capabilities"""
    print("=" * 60)
    print("CUSTOM PHOTO ROTATION SCREEN SAVER - LAYOUT DEMO")
    print("=" * 60)
    
    # Simulate different screen resolutions
    screen_configs = [
        (1920, 1080, "Full HD"),
        (2560, 1440, "2K/QHD"),
        (3840, 2160, "4K/UHD")
    ]
    
    for width, height, name in screen_configs:
        print(f"\n📺 {name} Display ({width}x{height})")
        print("-" * 40)
        
        # Create layout manager for this resolution
        layout_manager = LayoutManager(width, height)
        
        # Show available layouts
        available_layouts = layout_manager.get_available_layout_names()
        print(f"Available layouts: {', '.join(available_layouts)}")
        print(f"Total layouts: {layout_manager.get_layout_count()}")
        
        # Test each layout
        for i, layout_name in enumerate(available_layouts):
            print(f"\n  🔄 Testing {layout_name} layout (Index {i}):")
            
            # Set the layout
            if layout_manager.set_current_layout(layout_name):
                layout = layout_manager.get_current_layout()
                print(f"    ✓ Layout: {layout.name}")
                print(f"    ✓ Type: {layout.type.value}")
                print(f"    ✓ Dimensions: {layout.total_width}x{layout.total_height}")
                print(f"    ✓ Display Duration: {layout.display_duration/1000:.1f} seconds")
                
                # Show pane details
                for j, pane in enumerate(layout.panes, 1):
                    print(f"    📱 Pane {j} ({pane.name}):")
                    print(f"      Position: ({pane.x}, {pane.y})")
                    print(f"      Size: {pane.width}x{pane.height}")
                    print(f"      Photo categories: {', '.join(pane.photo_categories)}")
            else:
                print(f"    ✗ Failed to set {layout_name} layout")
        
        # Test layout rotation
        if layout_manager.get_layout_count() > 1:
            print(f"\n  🔄 Testing Layout Rotation:")
            print(f"    Current layout index: {layout_manager.get_current_layout_index()}")
            
            # Test rotation
            for rotation in range(min(3, layout_manager.get_layout_count())):
                next_layout = layout_manager.get_next_layout()
                if next_layout:
                    print(f"    Next layout: {next_layout.name}")
                    layout_manager.rotate_to_next_layout()
                    print(f"    Rotated to: {layout_manager.get_current_layout().name}")
                    print(f"    New index: {layout_manager.get_current_layout_index()}")
    
    print("\n" + "=" * 60)
    print("LAYOUT SYSTEM DEMO COMPLETE")
    print("=" * 60)


def demo_photo_organization():
    """Demonstrate how photos are organized by layout"""
    print("\n" + "=" * 60)
    print("PHOTO ORGANIZATION DEMO")
    print("=" * 60)
    
    # Simulate a 2K display
    width, height = 2560, 1440
    print(f"📺 Simulating {width}x{height} display")
    
    # Create layout manager
    layout_manager = LayoutManager(width, height)
    
    # Test all available layouts
    for layout_name in layout_manager.get_available_layout_names():
        print(f"\n🔄 Testing {layout_name} layout:")
        
        # Set the layout
        layout_manager.set_current_layout(layout_name)
        
        # Create photo selector
        photo_selector = PhotoSelector(layout_manager)
        
        # Simulate some photos by category
        simulated_photos = {
            "4:3_vertical": [
                PhotoMetadata("dummy_path_1.jpg"),  # Will have default dimensions
                PhotoMetadata("dummy_path_2.jpg"),
                PhotoMetadata("dummy_path_3.jpg")
            ],
            "square": [
                PhotoMetadata("dummy_path_4.jpg"),
                PhotoMetadata("dummy_path_5.jpg")
            ],
            "16:9_vertical": [
                PhotoMetadata("dummy_path_6.jpg"),
                PhotoMetadata("dummy_path_7.jpg")
            ],
            "16:9_landscape": [
                PhotoMetadata("dummy_path_8.jpg"),
                PhotoMetadata("dummy_path_9.jpg")
            ],
            "4:3_landscape": [
                PhotoMetadata("dummy_path_10.jpg"),
                PhotoMetadata("dummy_path_11.jpg")
            ]
        }
        
        # Set some dimensions for demo
        for category, photos in simulated_photos.items():
            for i, photo in enumerate(photos):
                if category == "4:3_vertical":
                    photo.width, photo.height = 1200, 1600
                elif category == "square":
                    photo.width, photo.height = 2000, 2000
                elif category == "16:9_vertical":
                    photo.width, photo.height = 1080, 1920
                elif category == "16:9_landscape":
                    photo.width, photo.height = 1920, 1080
                elif category == "4:3_landscape":
                    photo.width, photo.height = 1600, 1200
                photo.aspect_ratio_category = category
        
        # Organize photos by pane
        pane_photos = photo_selector.organize_photos_by_pane(simulated_photos)
        
        # Show organization results
        print(f"  📸 Photo Organization Results:")
        for pane_name, photos in pane_photos.items():
            print(f"\n    🖼️  {pane_name.capitalize()} Pane:")
            print(f"      Total photos: {len(photos)}")
            
            # Group by category
            by_category = {}
            for photo in photos:
                cat = photo.aspect_ratio_category
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(photo)
            
            for category, category_photos in by_category.items():
                print(f"      {category}: {len(category_photos)} photos")
    
    print("\n" + "=" * 60)


def demo_config_options():
    """Demonstrate configuration options"""
    print("\n" + "=" * 60)
    print("CONFIGURATION OPTIONS DEMO")
    print("=" * 60)
    
    # Create config manager
    config_manager = ConfigManager()
    
    print("📋 Current Configuration:")
    print(f"  Image Folder: {config_manager.get_image_folder()}")
    print(f"  Display Interval: {config_manager.get_display_interval()}ms")
    print(f"  Fullscreen: {config_manager.is_fullscreen()}")
    print(f"  Layout Type: {config_manager.get_layout_type()}")
    print(f"  Layout Rotation Enabled: {config_manager.is_layout_rotation_enabled()}")
    print(f"  Photo Layout Change Interval: {config_manager.get_photo_layout_change_interval()}ms")
    
    print("\n🔧 Available Layout Types:")
    print("  - auto: Automatically rotate through all available layouts")
    print("  - single_pane: Classic full-screen layout")
    print("  - dual_pane: Two-pane side-by-side layout")
    print("  - triple_pane: Three-pane horizontal layout")
    print("  - quad_pane: 2x2 grid layout")
    
    print("\n⚙️  Configuration Tips:")
    print("  - Set LAYOUT_TYPE=auto for dynamic layout rotation")
    print("  - Adjust PHOTO_LAYOUT_CHANGE_INTERVAL for faster/slower combined changes")
    print("  - Set LAYOUT_ROTATION_ENABLED=false to disable rotation")
    print("  - Layouts and photos change together every 15 seconds")
    
    print("\n" + "=" * 60)


def main():
    """Main demo function"""
    try:
        print("Starting Enhanced Layout System Demo...")
        print("This demo shows the new layout rotation capabilities and multiple layout modes.")
        print()
        
        # Demo 1: Layout system capabilities
        demo_layout_system()
        
        # Demo 2: Photo organization across layouts
        demo_photo_organization()
        
        # Demo 3: Configuration options
        demo_config_options()
        
        print("\n✅ Demo completed successfully!")
        print("\n🚀 New Features:")
        print("  - Multiple layout modes (Single, Dual, Triple, Quad Pane)")
        print("  - Automatic layout rotation")
        print("  - Smart photo placement for each layout")
        print("  - Configurable rotation intervals")
        print("\nTo run the actual screen saver with layout rotation:")
        print("1. Edit config.txt to set LAYOUT_TYPE=auto")
        print("2. Run: python main.py")
        print("3. Watch as layouts and photos automatically rotate together every 15 seconds!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
