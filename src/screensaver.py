"""
Main screen saver application module.
"""

import tkinter as tk
from PIL import Image, ImageTk
import os

from photo_classifier import PhotoClassifier
from photo_metadata import PhotoMetadata
from config_manager import ConfigManager
from layout_manager import LayoutManager
from photo_selector import PhotoSelector
from utils import find_image_files, calculate_display_dimensions, print_separator


class ScreenSaver:
    """Main screen saver application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Custom Photo Rotation Screen Saver")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.photo_classifier = PhotoClassifier()
        
        # Configure fullscreen
        if self.config_manager.is_fullscreen():
            self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # Bind exit events
        self.root.bind('<Escape>', lambda e: self.exit_screensaver())
        self.root.bind('<Button-1>', lambda e: self.exit_screensaver())
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.focus_set()  # Make sure the window can receive key events
        
        # Variables
        self.photos_by_category = {}
        self.photo_selector = None
        self.running = False
        self.layout_rotation_timer = None
        self.photo_rotation_timer = None
        self.is_in_photo_cycle = False  # Track if we're in a photo rotation cycle
        
        # Load config and start
        self.load_and_classify_photos()
    
    def load_and_classify_photos(self):
        """Load, classify, and organize photos by aspect ratio category"""
        image_folder = self.config_manager.get_image_folder()
        
        if not image_folder:
            self.show_error("No image folder configured. Please check config.txt file.")
            return
        
        # Validate folder
        is_valid, message = self.config_manager.validate_image_folder()
        if not is_valid:
            self.show_error(f"{message}\nPlease check config.txt file.")
            return
        
        print(f"Loading and classifying photos from: {image_folder}")
        
        # Find all image files
        image_files = find_image_files(image_folder)
        if not image_files:
            self.show_error(f"No supported images found in: {image_folder}\nSupported formats: JPG, JPEG, PNG")
            return
        
        # Classify photos
        self.photos_by_category = {}
        for filepath in image_files:
            photo_metadata = PhotoMetadata(filepath)
            
            # Classify the photo
            category = self.photo_classifier.classify_photo(photo_metadata.width, photo_metadata.height)
            photo_metadata.aspect_ratio_category = category
            
            # Organize by category
            if category not in self.photos_by_category:
                self.photos_by_category[category] = []
            self.photos_by_category[category].append(photo_metadata)
        
        # Print classification summary
        self.print_classification_summary()
        
        # Initialize layout system
        self.initialize_layout_system()
        
        # Start slideshow if photos found
        total_photos = sum(len(photos) for photos in self.photos_by_category.values())
        if total_photos > 0:
            self.start_slideshow()
        else:
            self.show_error(f"No supported images found in: {image_folder}")
    
    def initialize_layout_system(self):
        """Initialize the layout system based on configuration"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        print(f"Screen dimensions: {screen_width}x{screen_height}")
        
        # Create layout manager
        self.layout_manager = LayoutManager(screen_width, screen_height)
        
        # Get configured layout type
        layout_type = self.config_manager.get_layout_type()
        print(f"Configured layout type: {layout_type}")
        
        # Configure layout rotation
        rotation_enabled = self.config_manager.is_layout_rotation_enabled()
        self.layout_manager.set_layout_rotation_enabled(rotation_enabled)
        
        if rotation_enabled:
            print(f"Layout rotation enabled with {self.layout_manager.get_layout_count()} layouts available")
            print(f"Available layouts: {', '.join(self.layout_manager.get_available_layout_names())}")
        
        # Set initial layout
        if layout_type == "auto":
            # Start with first available layout
            if self.layout_manager.get_available_layouts():
                self.layout_manager.set_current_layout_by_index(0)
                print(f"Auto mode: Starting with layout: {self.layout_manager.get_current_layout().name}")
            else:
                print("No layouts available")
                return
        else:
            # Check if specific layout is available
            if not self.layout_manager.can_use_layout(layout_type):
                print(f"Layout '{layout_type}' not available for this screen resolution")
                print(f"Available layouts: {self.layout_manager.get_available_layout_names()}")
                # Fallback to first available layout
                if self.layout_manager.get_available_layouts():
                    self.layout_manager.set_current_layout_by_index(0)
                    print(f"Fallback to layout: {self.layout_manager.get_current_layout().name}")
                else:
                    print("No layouts available")
                    return
            else:
                self.layout_manager.set_current_layout(layout_type)
                print(f"Using layout: {self.layout_manager.get_current_layout().name}")
        
        # Create photo selector
        self.photo_selector = PhotoSelector(self.layout_manager)
        
        # Organize photos by pane
        pane_photos = self.photo_selector.organize_photos_by_pane(self.photos_by_category)
        
        # Print pane summary
        self.print_pane_summary()
    
    def print_pane_summary(self):
        """Print a summary of photos available for each pane"""
        if not self.photo_selector:
            return
        
        pane_summary = self.photo_selector.get_pane_summary()
        
        print_separator()
        print("Layout Pane Summary:")
        for pane_name, info in pane_summary.items():
            categories_str = ", ".join(info['categories'])
            dimensions = info['dimensions']
            if dimensions:
                x, y, w, h = dimensions
                print(f"  {pane_name.capitalize()} Pane ({w}x{h}): {info['total_photos']} photos")
                print(f"    Categories: {categories_str}")
            else:
                print(f"  {pane_name.capitalize()} Pane: {info['total_photos']} photos")
                print(f"    Categories: {categories_str}")
        print_separator()
    
    def print_classification_summary(self):
        """Print a summary of photo classification results"""
        total_photos = sum(len(photos) for photos in self.photos_by_category.values())
        
        print_separator()
        print("Photo Classification Summary:")
        print(f"Total photos found: {total_photos}")
        
        # Sort categories by photo count (descending)
        sorted_categories = sorted(
            self.photos_by_category.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for category, photos in sorted_categories:
            display_name = self.photo_classifier.get_category_display_name(category)
            print(f"  {display_name}: {len(photos)} photos")
        
        print_separator()
    
    def show_error(self, message):
        """Display error message on screen"""
        error_label = tk.Label(
            self.root,
            text=message,
            font=('Arial', 16),
            fg='red',
            bg='black'
        )
        error_label.pack(expand=True)
        
        # Add exit instructions
        exit_label = tk.Label(
            self.root,
            text="Press any key, click, or Escape to exit",
            font=('Arial', 12),
            fg='white',
            bg='black'
        )
        exit_label.pack(pady=20)
    
    def start_slideshow(self):
        """Start the image slideshow"""
        if not self.photo_selector:
            return
            
        self.running = True
        
        # Check if we have photos for any pane
        has_photos = any(self.photo_selector.has_photos_for_pane(pane_name) 
                        for pane_name in self.photo_selector.get_all_pane_names())
        
        if has_photos:
            self.show_next_photos()
            
            # Start layout rotation if enabled
            if self.layout_manager.is_layout_rotation_enabled():
                self.start_layout_rotation()
        else:
            self.show_error("No photos available for the current layout")
    
    def start_layout_rotation(self):
        """Start automatic layout rotation"""
        if not self.layout_manager.is_layout_rotation_enabled():
            return
        
        rotation_interval = self.config_manager.get_photo_layout_change_interval()
        print(f"Photo layout changes will occur every {rotation_interval/1000:.1f} seconds")
        
        # Schedule first combined rotation after the initial photo display period
        # This ensures both layout and photos change together
        initial_delay = self.config_manager.get_display_interval()
        self.layout_rotation_timer = self.root.after(initial_delay + rotation_interval, self.rotate_layout_and_photos)
    
    def rotate_layout_and_photos(self):
        """Rotate to the next layout AND show new photos simultaneously"""
        if not self.running or not self.layout_manager.is_layout_rotation_enabled():
            return
        
        # Get next layout
        next_layout = self.layout_manager.rotate_to_next_layout()
        if next_layout:
            if self.config_manager.is_debug_mode_enabled():
                print(f"🔄 Combined rotation: {self.layout_manager.get_current_layout().name} → {next_layout.name}")
            else:
                print(f"Rotating to layout: {next_layout.name}")
            
            # Reorganize photos for new layout
            self.photo_selector.organize_photos_by_pane(self.photos_by_category)
            
            # Print new pane summary
            self.print_pane_summary()
            
            # Show photos in new layout
            self.show_next_photos()
            
            # Schedule next combined rotation
            rotation_interval = self.config_manager.get_photo_layout_change_interval()
            self.layout_rotation_timer = self.root.after(rotation_interval, self.rotate_layout_and_photos)
            
            if self.config_manager.is_debug_mode_enabled():
                print(f"🔄 Combined rotation scheduled in {rotation_interval/1000:.1f} seconds")
    
    def rotate_layout(self):
        """Rotate to the next layout (legacy method - kept for compatibility)"""
        self.rotate_layout_and_photos()
    
    def show_next_photos(self):
        """Display the next photos for all panes"""
        if not self.running or not self.photo_selector:
            return
        
        try:
            # Clear existing content
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Get current layout
            layout = self.layout_manager.get_current_layout()
            if not layout:
                return
            
            # Get unique photos for all panes simultaneously
            pane_photos = self.photo_selector.get_unique_photos_for_all_panes()
            
            # Display photos for each pane
            for pane in layout.panes:
                if pane.name in pane_photos:
                    self.display_photo_in_pane(pane, pane_photos[pane.name])
            
            # No need to schedule photo rotation - photos change with layouts
            if self.config_manager.is_debug_mode_enabled():
                print(f"📸 Photos displayed - will change with next layout rotation")
                
        except Exception as e:
            print(f"Error displaying photos: {e}")
            self.next_photos()
    
    def display_photo_in_pane(self, pane, photo_metadata=None):
        """Display a photo in a specific pane"""
        try:
            # Get photo metadata if not provided
            if photo_metadata is None:
                photo_metadata = self.photo_selector.get_next_photo_for_pane(pane.name)
            
            if not photo_metadata:
                return
            
            # Load image
            image = Image.open(photo_metadata.filepath)
            
            # Calculate display dimensions for this pane
            target_width, target_height = calculate_display_dimensions(
                pane.width, pane.height,
                photo_metadata.width, photo_metadata.height
            )
            
            # Resize image
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Add debug overlay if enabled
            if self.config_manager.is_debug_mode_enabled():
                image = self.add_debug_overlay(image, photo_metadata, pane)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Create frame for this pane
            pane_frame = tk.Frame(self.root, bg='black')
            pane_frame.place(x=pane.x, y=pane.y, width=pane.width, height=pane.height)
            
            # Create and configure image label
            image_label = tk.Label(pane_frame, image=photo, bg='black')
            image_label.photo = photo  # Keep a reference
            image_label.pack(expand=True, fill='both')
            
        except Exception as e:
            print(f"Error displaying photo in pane {pane.name}: {e}")
    
    def add_debug_overlay(self, image, photo_metadata, pane):
        """Add debug metadata overlay to the image"""
        try:
            from PIL import ImageDraw, ImageFont
            
            # Create a copy of the image to draw on
            overlay_image = image.copy()
            draw = ImageDraw.Draw(overlay_image)
            
            # Try to use a default font, fallback to basic if not available
            try:
                # Try to use a system font
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", 16)
                except:
                    font = ImageFont.load_default()
            
            # Prepare debug text
            debug_lines = [
                f"Pane: {pane.name}",
                f"File: {os.path.basename(photo_metadata.filepath)}",
                f"Category: {photo_metadata.aspect_ratio_category}",
                f"Original: {photo_metadata.width}x{photo_metadata.height}",
                f"Display: {pane.width}x{pane.height}",
                f"Date: {photo_metadata.get_formatted_date()}",
                f"Size: {photo_metadata.get_file_size_mb():.1f}MB"
            ]
            
            # Calculate text positioning (top-left corner with some padding)
            padding = 10
            line_height = 20
            y_position = padding
            
            # Draw semi-transparent background for text
            max_line_width = max(draw.textlength(line, font=font) for line in debug_lines)
            text_bg_width = int(max_line_width) + 20
            text_bg_height = len(debug_lines) * line_height + 20
            
            # Create semi-transparent overlay
            overlay_bg = Image.new('RGBA', (text_bg_width, text_bg_height), (0, 0, 0, 128))
            overlay_image.paste(overlay_bg, (padding, padding), overlay_bg)
            
            # Draw text lines
            for i, line in enumerate(debug_lines):
                y = y_position + (i * line_height)
                draw.text((padding + 10, y), line, fill=(255, 255, 255, 255), font=font)
            
            return overlay_image
            
        except Exception as e:
            print(f"Error adding debug overlay: {e}")
            return image  # Return original image if overlay fails
    
    def next_photos(self):
        """Move to the next set of photos (legacy method - kept for debug mode Enter key)"""
        if not self.running:
            return
        
        # In the new system, this triggers a combined layout+photo rotation
        if self.layout_manager.is_layout_rotation_enabled():
            if self.config_manager.is_debug_mode_enabled():
                print("🔄 Debug mode: Manual trigger of combined rotation")
            
            # Trigger combined rotation immediately
            self.rotate_layout_and_photos()
        else:
            # If no layout rotation, just show next photos
            self.show_next_photos()
    
    def on_key_press(self, event):
        """Handle key press events"""
        # In debug mode, Enter key advances to next photo rotation
        if self.config_manager.is_debug_mode_enabled() and event.keysym == 'Return':
            print("🔄 Debug mode: Advancing to next photo rotation...")
            self.next_photos()
        else:
            # Any other key exits the screensaver
            self.exit_screensaver()
    
    def exit_screensaver(self):
        """Exit the screen saver"""
        self.running = False
        
        # Cancel layout rotation timer
        if self.layout_rotation_timer:
            self.root.after_cancel(self.layout_rotation_timer)
            self.layout_rotation_timer = None
        
        # Photo rotation timer is no longer used in the new system
        # but keep the variable for potential future use
        
        self.root.quit()
    
    def run(self):
        """Start the screen saver"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.exit_screensaver()
