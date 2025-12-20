"""
Main screen saver application module.
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import random

from photo_classifier import PhotoClassifier
from photo_metadata import PhotoMetadata
from config_manager import ConfigManager
from layout_manager import LayoutManager
from photo_selector import PhotoSelector
from utils import find_image_files, calculate_display_dimensions, calculate_crop_dimensions, print_separator


class ScreenSaver:
    """Main screen saver application class"""
    
    def __init__(self):
        # Set DPI awareness BEFORE creating Tkinter window
        self._set_dpi_awareness()
        
        self.root = tk.Tk()        
        self.root.title("Custom Photo Rotation Screen Saver")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.photo_classifier = PhotoClassifier()
        
        # Set window size to actual resolution before fullscreen
        actual_width, actual_height = self.get_actual_screen_resolution()
        self.root.geometry(f"{actual_width}x{actual_height}")
        
        # Configure fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # Bind exit events
        self.root.bind('<Escape>', lambda e: self.exit_screensaver())
        self.root.bind('<Button-1>', lambda e: self.exit_screensaver())
        self.root.bind('<KeyPress>', self.on_key_press)
        
        # Ensure window comes to foreground and can receive input
        # Schedule after window is created to ensure effectiveness
        self.root.after(100, self._bring_to_foreground)
        self.root.focus_set()  # Make sure the window can receive key events
        
        # Variables
        self.photos_by_category = {}
        self.photo_selector = None
        self.running = False
        self.layout_rotation_timer = None
        self.photo_rotation_timer = None
        self.is_in_photo_cycle = False  # Track if we're in a photo rotation cycle
        self.last_rotation_time = None  # Track timing for debugging
        self.debug_overlay_visible = False  # Toggle for debug overlay visibility
        
        # Enhanced debug logging variables
        self.is_collecting_issue_text = False  # Track if we're collecting issue description
        self.issue_text_buffer = ""  # Buffer for collecting issue description text
        self.issue_start_time = None  # When issue reporting started
        self.currently_displayed_photos = {}  # Store photos that are currently displayed on screen
        
        # Load config and start
        self.load_and_classify_photos()

    def _set_dpi_awareness(self):
        """Set DPI awareness for the application on Windows"""
        try:
            import ctypes
            import platform
            
            if platform.system() != 'Windows':
                return
            
            # Try Windows 10 1703+ method first (best)
            try:
                # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
                print("✅ DPI Awareness set: Per-Monitor V2")
                return
            except:
                pass
            
            # Try Windows 8.1+ method
            try:
                # PROCESS_PER_MONITOR_DPI_AWARE = 2
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
                print("✅ DPI Awareness set: Per-Monitor")
                return
            except:
                pass
            
            # Fallback to older Windows method
            try:
                ctypes.windll.user32.SetProcessDPIAware()
                print("✅ DPI Awareness set: System DPI Aware")
                return
            except Exception as e:
                print(f"⚠️ Could not set DPI awareness: {e}")
                
        except Exception as e:
            print(f"⚠️ DPI awareness setup failed: {e}")

    def _bring_to_foreground(self):
        """Bring the window to the foreground and ensure it has focus"""
        try:
            import ctypes
            import platform
            
            # Get the window handle
            hwnd = self.root.winfo_id()
            
            if platform.system() == 'Windows':
                # Use Windows API to bring window to foreground
                try:
                    # SetForegroundWindow - brings window to foreground
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    print("✅ Window brought to foreground using SetForegroundWindow")
                except Exception as e:
                    print(f"⚠️ SetForegroundWindow failed: {e}")
                
                try:
                    # ShowWindow with SW_SHOW to ensure window is visible
                    # SW_SHOW = 5
                    ctypes.windll.user32.ShowWindow(hwnd, 5)
                    print("✅ Window shown using ShowWindow(SW_SHOW)")
                except Exception as e:
                    print(f"⚠️ ShowWindow failed: {e}")
                
                try:
                    # SetActiveWindow - sets the window as active
                    ctypes.windll.user32.SetActiveWindow(hwnd)
                    print("✅ Window set as active using SetActiveWindow")
                except Exception as e:
                    print(f"⚠️ SetActiveWindow failed: {e}")
                
                try:
                    # BringWindowToTop - another method to bring to top
                    ctypes.windll.user32.BringWindowToTop(hwnd)
                    print("✅ Window brought to top using BringWindowToTop")
                except Exception as e:
                    print(f"⚠️ BringWindowToTop failed: {e}")
            else:
                # For non-Windows systems, use Tkinter methods
                self.root.lift()
                self.root.attributes('-topmost', True)
                self.root.after_idle(lambda: self.root.attributes('-topmost', False))
                print("✅ Window brought to foreground on non-Windows system")
                
        except Exception as e:
            print(f"⚠️ Error bringing window to foreground: {e}")

    def get_actual_screen_resolution(self):
        """Get actual screen resolution after DPI awareness is set"""
        # After setting DPI awareness, Tkinter reports actual resolution
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        
        print(f"🖥️  Screen resolution: {width}x{height}")
        return width, height
    
    def _add_triple_vertical_layout_for_4k(self, screen_width, screen_height):
        """Manually add Triple Vertical layout for 4K displays with DPI scaling"""
        try:
            from layout_manager import Layout, LayoutType, Pane
            
            # Calculate pane dimensions using Tkinter resolution
            pane_width = screen_width // 3
            
            triple_vertical_layout = Layout(
                name="Triple Vertical",
                type=LayoutType.TRIPLE_PANE,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=pane_width,
                        height=screen_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
                        name="left"
                    ),
                    Pane(
                        x=pane_width, y=0,
                        width=pane_width,
                        height=screen_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
                        name="center"
                    ),
                    Pane(
                        x=pane_width * 2, y=0,
                        width=pane_width,
                        height=screen_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
                        name="right"
                    )
                ],
                total_width=screen_width,
                total_height=screen_height,
                display_duration=30000  # 30 seconds
            )
            
            # Add to available layouts
            self.layout_manager.available_layouts.append(triple_vertical_layout)
            print(f"✅ Added Triple Vertical layout with Tkinter dimensions: {pane_width}x{screen_height} per pane")
            
        except Exception as e:
            print(f"❌ Failed to add Triple Vertical layout for 4K: {e}")
    
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
        
        # Start initial transition if photos found
        total_photos = sum(len(photos) for photos in self.photos_by_category.values())
        if total_photos > 0:
            self.show_initial_transition()
        else:
            self.show_error(f"No supported images found in: {image_folder}")
    
    def initialize_layout_system(self):
        """Initialize the layout system based on configuration"""
        # Get screen resolution
        screen_width, screen_height = self.get_actual_screen_resolution()
        
        print(f"🖥️  Screen resolution: {screen_width}x{screen_height}")
        
        # Get layout weights from config (optional - uses defaults if not configured)
        layout_weights = self.config_manager.get_layout_weights()
        
        # Use screen resolution directly for layout calculations
        self.layout_manager = LayoutManager(screen_width, screen_height, layout_weights)
        print(f"🖥️  Layout manager created with: {screen_width}x{screen_height}")
        
        # Store scaling factor for photo display
        self.display_scale_x = 1.0
        self.display_scale_y = 1.0
        print(f"🔍  Display scaling: {self.display_scale_x:.3f}x, {self.display_scale_y:.3f}y")
        
        # Get configured layout type
        layout_type = self.config_manager.get_layout_type()
        print(f"Configured layout type: {layout_type}")
        
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
        
        # Create photo selector with time weighting multiplier from config
        time_weighting_multiplier = self.config_manager.get_time_weighting_multiplier()
        self.photo_selector = PhotoSelector(self.layout_manager, time_weighting_multiplier)
        
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
    
    def show_initial_transition(self):
        """Show initial black screen with dissolve transition to a random 16:9 landscape photo"""
        try:
            # Clear any existing content
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Ensure black background
            self.root.configure(bg='black')
            
            # Check if we have 16:9 landscape photos
            landscape_16_9_photos = self.photos_by_category.get("16:9_landscape", [])
            
            if landscape_16_9_photos:
                # Select a random 16:9 landscape photo
                import random
                self.initial_photo_metadata = random.choice(landscape_16_9_photos)
                
                print(f"🎬 Initial transition: Using 16:9 landscape photo: {os.path.basename(self.initial_photo_metadata.filepath)}")
                
                # Calculate display dimensions to fit the screen while maintaining aspect ratio
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                # Calculate scale to fit the image within the screen
                scale_x = screen_width / self.initial_photo_metadata.width
                scale_y = screen_height / self.initial_photo_metadata.height
                scale = min(scale_x, scale_y)  # Use min to ensure image fits within screen
                
                target_width = int(self.initial_photo_metadata.width * scale)
                target_height = int(self.initial_photo_metadata.height * scale)
                
                # Create a label for the photo (initially black)
                self.initial_photo_label = tk.Label(self.root, bg='black')
                self.initial_photo_label.place(
                    x=(screen_width - target_width) // 2,  # Center horizontally
                    y=(screen_height - target_height) // 2,  # Center vertically
                    width=target_width,
                    height=target_height
                )
                
                # Start the dissolve transition
                self.start_dissolve_transition()
            else:
                print("⚠️  No 16:9 landscape photos available, proceeding with normal flow")
                self.initial_transition_complete = True
                self.start_slideshow()
                
        except Exception as e:
            print(f"Error in initial transition: {e}")
            # Fallback to normal flow
            self.initial_transition_complete = True
            self.start_slideshow()
    
    def start_dissolve_transition(self):
        """Start the dissolve transition from 0% to 100% opacity over 0.25 seconds"""
        try:
            # Store the original image for alpha blending
            self.original_image = Image.open(self.initial_photo_metadata.filepath)
            
            # Calculate display dimensions to fit the screen while maintaining aspect ratio
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calculate scale to fit the image within the screen
            scale_x = screen_width / self.initial_photo_metadata.width
            scale_y = screen_height / self.initial_photo_metadata.height
            scale = min(scale_x, scale_y)  # Use min to ensure image fits within screen
            
            target_width = int(self.initial_photo_metadata.width * scale)
            target_height = int(self.initial_photo_metadata.height * scale)
            
            # Resize the original image
            self.original_image = self.original_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Calculate step size for smooth transition (0.25 seconds = 250ms)
            # Use 50 steps for smoother animation (5ms per step)
            total_steps = 50
            step_delay = 5  # milliseconds (5ms * 50 = 250ms = 0.25 seconds)
            
            def animate_transition(step=0):
                if step >= total_steps:
                    # Transition complete
                    self.initial_transition_complete = True
                    print("🎬 Initial transition complete, starting normal slideshow")
                    # Add a small pause to make the final image visible
                    self.root.after(500, self.start_slideshow)  # 0.5 second pause
                    return
                
                # Calculate current opacity (0.0 to 1.0)
                current_opacity = step / total_steps
                
                # Debug output for transition progress
                if step % 10 == 0 or step == total_steps - 1:  # Log every 10th step and final step
                    print(f"🎬 Transition step {step}/{total_steps}: opacity {current_opacity:.2f}")
                
                # Create a new image with the current opacity
                # We'll blend the image with a black background based on opacity
                if current_opacity < 1.0:
                    # Create a black background image
                    black_bg = Image.new('RGB', (target_width, target_height), 'black')
                    
                    # Blend the image with black background based on opacity
                    blended_image = Image.blend(black_bg, self.original_image, current_opacity)
                    
                    # Convert to PhotoImage and update the label
                    photo = ImageTk.PhotoImage(blended_image)
                    self.initial_photo_label.configure(image=photo)
                    self.initial_photo_label.photo = photo  # Keep a reference
                else:
                    # At 100% opacity, show the original image
                    photo = ImageTk.PhotoImage(self.original_image)
                    self.initial_photo_label.configure(image=photo)
                    self.initial_photo_label.photo = photo  # Keep a reference
                
                # Schedule next step
                self.root.after(step_delay, lambda: animate_transition(step + 1))
            
            # Start the animation
            animate_transition()
            
        except Exception as e:
            print(f"Error in dissolve transition: {e}")
            # Fallback to normal flow
            self.initial_transition_complete = True
            self.start_slideshow()
    
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
            
            # Start layout rotation
            self.start_layout_rotation()
        else:
            self.show_error("No photos available for the current layout")
    
    def start_layout_rotation(self):
        """Start automatic layout rotation"""
        rotation_interval = self.config_manager.get_change_interval()
        print(f"Layout and photo changes will occur every {rotation_interval/1000:.1f} seconds")
        
        # Schedule first combined rotation using the same interval as subsequent rotations
        # This creates consistent timing throughout the session
        self.layout_rotation_timer = self.root.after(rotation_interval, self.rotate_layout_and_photos)
        
        print(f"🔄 First rotation scheduled in {rotation_interval/1000:.1f} seconds")
    
    def rotate_layout_and_photos(self):
        """Rotate to the next layout AND show new photos simultaneously"""
        if not self.running:
            return
        
        # Cancel any existing timer to prevent overlapping rotations
        if self.layout_rotation_timer:
            self.root.after_cancel(self.layout_rotation_timer)
            self.layout_rotation_timer = None
            print("🔄 Cancelled previous rotation timer")
        
        # Track rotation timing for debugging
        current_time = time.time()
        if self.last_rotation_time:
            elapsed = current_time - self.last_rotation_time
            print(f"⏱️  Time since last rotation: {elapsed:.2f} seconds")
        self.last_rotation_time = current_time
        
        # Get next layout
        next_layout = self.layout_manager.rotate_to_next_layout()
        if next_layout:
            print(f"🔄 Combined rotation: {self.layout_manager.get_current_layout().name} → {next_layout.name}")
            
            # Reorganize photos for new layout
            self.photo_selector.organize_photos_by_pane(self.photos_by_category)
            
            # Print new pane summary
            self.print_pane_summary()
            
            # Show photos in new layout
            self.show_next_photos()
            
            # Schedule next combined rotation
            rotation_interval = self.config_manager.get_change_interval()
            self.layout_rotation_timer = self.root.after(rotation_interval, self.rotate_layout_and_photos)
            
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
            
            # CRITICAL FIX: Ensure every pane has a photo - use fallback logic if needed
            for pane in layout.panes:
                if pane.name not in pane_photos or pane_photos[pane.name] is None:
                    # Pane is missing a photo - find one using fallback logic
                    fallback_photo = self._get_fallback_photo_for_pane(pane)
                    if fallback_photo:
                        pane_photos[pane.name] = fallback_photo
                        print(f"⚠️  Using fallback photo for {pane.name} pane: {os.path.basename(fallback_photo.filepath)}")
                    else:
                        print(f"❌ CRITICAL: No photo available for {pane.name} pane!")
            
            # Store the photos that are about to be displayed for refresh operations
            self.currently_displayed_photos = pane_photos.copy()
            
            # Display photos for each pane
            for pane in layout.panes:
                if pane.name in pane_photos and pane_photos[pane.name]:
                    photo = pane_photos[pane.name]
                    # Log aspect ratio error for debugging
                    target_ratio, actual_ratio, category_error = self.get_detailed_aspect_ratio_info(photo)
                    display_crop = self.calculate_display_crop_error(photo, pane)
                    is_ultra_wide = photo.aspect_ratio_category == "ultra_wide"
                    display_method = "Display Letterbox" if is_ultra_wide else "Display Crop"
                    print(f"📊 {pane.name} pane: {photo.aspect_ratio_category} photo ({photo.width}x{photo.height}) - Category Error: {target_ratio:.3f} - {actual_ratio:.3f} = {category_error:.3f}, {display_method}: {display_crop:.4f}")
                    self.display_photo_in_pane(pane, photo)
            
            # No need to schedule photo rotation - photos change with layouts
            print(f"📸 Photos displayed - will change with next layout rotation")
                
        except Exception as e:
            print(f"Error displaying photos: {e}")
            self.next_photos()
    
    def _get_fallback_photo_for_pane(self, pane):
        """Get a fallback photo for a pane that couldn't find a suitable photo"""
        try:
            # Try to find any available photo from any category that this pane accepts
            for category in pane.photo_categories:
                if category in self.photos_by_category and self.photos_by_category[category]:
                    available_photos = self.photos_by_category[category]
                    if available_photos:
                        # Return a random photo from this category
                        return random.choice(available_photos)
            
            # If no photos found in preferred categories, try any category
            for category in self.photos_by_category:
                if self.photos_by_category[category]:
                    return random.choice(self.photos_by_category[category])
            
            # No photos available at all
            return None
            
        except Exception as e:
            print(f"Error getting fallback photo for {pane.name}: {e}")
            return None
    
    def refresh_display(self):
        """Refresh the display with current photos and debug overlay state (no new photos)"""
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
            
            # Use the photos that are currently displayed on screen
            if hasattr(self, 'currently_displayed_photos') and self.currently_displayed_photos:
                pane_photos = self.currently_displayed_photos.copy()
            else:
                # Fallback: get current photos from photo selector
                pane_photos = self.photo_selector.get_current_photos_for_all_panes()
            
            # Display current photos for each pane
            for pane in layout.panes:
                if pane.name in pane_photos:
                    photo = pane_photos[pane.name]
                    # Log aspect ratio error for debugging
                    target_ratio, actual_ratio, category_error = self.get_detailed_aspect_ratio_info(photo)
                    display_crop = self.calculate_display_crop_error(photo, pane)
                    is_ultra_wide = photo.aspect_ratio_category == "ultra_wide"
                    display_method = "Display Letterbox" if is_ultra_wide else "Display Crop"
                    print(f"📊 {pane.name} pane: {photo.aspect_ratio_category} photo ({photo.width}x{photo.height}) - Category Error: {target_ratio:.3f} - {actual_ratio:.3f} = {category_error:.3f}, {display_method}: {display_crop:.4f}")
                    self.display_photo_in_pane(pane, photo)
            
            print(f"🔄 Display refreshed with current photos and debug overlay {'ON' if self.debug_overlay_visible else 'OFF'}")
                
        except Exception as e:
            print(f"Error refreshing display: {e}")
    

    def display_photo_in_pane(self, pane, photo_metadata=None):
        """Display a photo in a specific pane"""
        try:
            # Get photo metadata if not provided
            if photo_metadata is None:
                photo_metadata = self.photo_selector.get_next_photo_for_pane(pane.name)
            
            if not photo_metadata:
                print(f"⚠️  No photo metadata for {pane.name} pane")
                return
            
            # Load image
            image = Image.open(photo_metadata.filepath)
            original_size = image.size
            
            # Scale pane dimensions from actual resolution to Tkinter resolution
            display_pane_width = int(pane.width * self.display_scale_x)
            display_pane_height = int(pane.height * self.display_scale_y)
            
            print(f"🖼️  STARTING display_photo_in_pane for [{pane.name}]")
            print(f"🖼️  [{pane.name}] Pane target: {display_pane_width}x{display_pane_height}, Original image: {original_size}")
            print(f"🖼️  [{pane.name}] display_scale_x={self.display_scale_x}, display_scale_y={self.display_scale_y}")
            
            # Handle ultra-wide photos differently - maintain aspect ratio without cropping
            is_ultra_wide = photo_metadata.aspect_ratio_category == "ultra_wide"
            
            if is_ultra_wide:
                # Ultra-wide photos: maintain aspect ratio (may have letterboxing)
                target_width, target_height = calculate_display_dimensions(
                    display_pane_width, display_pane_height,
                    photo_metadata.width, photo_metadata.height,
                    stretch_to_fill=False  # Don't stretch ultra-wide photos
                )
                print(f"🖼️  [{pane.name}] Ultra-wide: Resizing to {target_width}x{target_height} (maintain aspect ratio)")
                # Resize image maintaining aspect ratio
                image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            else:
                # All other photos: use cropping to maintain aspect ratio while filling the pane
                # Calculate scale factors for both dimensions
                scale_x = display_pane_width / photo_metadata.width
                scale_y = display_pane_height / photo_metadata.height
                scale = max(scale_x, scale_y)
                
                print(f"🖼️  [{pane.name}] Scale factors: x={scale_x:.4f}, y={scale_y:.4f}, max={scale:.4f}")
                
                # Calculate scaled dimensions using ceiling to ensure we cover the entire pane
                # This prevents gaps due to integer rounding
                import math
                scaled_width = math.ceil(photo_metadata.width * scale)
                scaled_height = math.ceil(photo_metadata.height * scale)
                
                # Ensure scaled dimensions are at least as large as the pane
                # This is critical for proper cropping
                scaled_width = max(scaled_width, display_pane_width)
                scaled_height = max(scaled_height, display_pane_height)
                
                print(f"🖼️  [{pane.name}] Scaled image: {scaled_width}x{scaled_height} (from {photo_metadata.width}x{photo_metadata.height})")
                
                # Resize image
                image = image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
                print(f"🖼️  [{pane.name}] After resize: {image.size}")
                
                # Calculate crop position to center the image
                crop_x = (scaled_width - display_pane_width) // 2
                crop_y = (scaled_height - display_pane_height) // 2
                
                print(f"🖼️  [{pane.name}] Initial crop position: x={crop_x}, y={crop_y}")
                
                # Ensure crop coordinates are valid and non-negative
                crop_x = max(0, crop_x)
                crop_y = max(0, crop_y)
                
                # Ensure the crop box doesn't exceed image bounds
                crop_right = min(crop_x + display_pane_width, scaled_width)
                crop_bottom = min(crop_y + display_pane_height, scaled_height)
                
                # Validate crop box
                if crop_right <= crop_x or crop_bottom <= crop_y:
                    print(f"❌ [{pane.name}] Invalid crop box! x:{crop_x}-{crop_right}, y:{crop_y}-{crop_bottom}")
                    # Fallback: use center crop
                    crop_x = max(0, (scaled_width - display_pane_width) // 2)
                    crop_y = max(0, (scaled_height - display_pane_height) // 2)
                    crop_right = min(crop_x + display_pane_width, scaled_width)
                    crop_bottom = min(crop_y + display_pane_height, scaled_height)
                    print(f"🔧 [{pane.name}] Fallback crop box: x:{crop_x}-{crop_right}, y:{crop_y}-{crop_bottom}")
                
                print(f"🖼️  [{pane.name}] Final crop box: ({crop_x}, {crop_y}, {crop_right}, {crop_bottom})")
                
                # Crop the image to fit the pane exactly
                image = image.crop((crop_x, crop_y, crop_right, crop_bottom))
                print(f"🖼️  [{pane.name}] After crop: {image.size}")
                
                # If the cropped image is smaller than the pane (shouldn't happen with max scale), pad it
                if image.size != (display_pane_width, display_pane_height):
                    print(f"⚠️  [{pane.name}] Cropped image {image.size} != target {(display_pane_width, display_pane_height)}, padding...")
                    # Create a new image with the correct size and paste the cropped image
                    padded_image = Image.new('RGB', (display_pane_width, display_pane_height), 'black')
                    # Calculate position to center the cropped image
                    pad_x = (display_pane_width - image.size[0]) // 2
                    pad_y = (display_pane_height - image.size[1]) // 2
                    padded_image.paste(image, (pad_x, pad_y))
                    image = padded_image
                    print(f"🖼️  [{pane.name}] After padding: {image.size}")
            
            # Verify final image size
            if image.size[0] <= 0 or image.size[1] <= 0:
                print(f"❌ [{pane.name}] ERROR: Final image has invalid size: {image.size}")
                return
            
            # Add debug overlay if enabled
            if self.debug_overlay_visible:
                image = self.add_debug_overlay(image, photo_metadata, pane)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Create frame for this pane using scaled coordinates and dimensions
            scaled_pane_x = int(pane.x * self.display_scale_x)
            scaled_pane_y = int(pane.y * self.display_scale_y)
            pane_frame = tk.Frame(self.root, bg='black')
            pane_frame.place(x=scaled_pane_x, y=scaled_pane_y, width=display_pane_width, height=display_pane_height)
            
            # Create and configure image label
            image_label = tk.Label(pane_frame, image=photo, bg='black')
            image_label.photo = photo  # Keep a reference
            image_label.pack(expand=True, fill='both')
            
            print(f"✅ [{pane.name}] Successfully displayed image {image.size}")
            
        except Exception as e:
            import traceback
            print(f"❌ Error displaying photo in pane {pane.name}: {e}")
            traceback.print_exc()
    
    def calculate_aspect_ratio_error(self, photo_metadata):
        """Calculate how far off the photo's aspect ratio is from its classified category"""
        try:
            # Get the photo's actual aspect ratio
            actual_ratio = photo_metadata.width / photo_metadata.height
            category = photo_metadata.aspect_ratio_category
            
            # Define target ratios for each category
            target_ratios = {
                "square": 1.0,
                "4:3_landscape": 4/3,
                "4:3_vertical": 3/4,
                "16:9_landscape": 16/9,
                "16:9_vertical": 9/16,
                "ultra_wide": 21/9
            }
            
            if category in target_ratios:
                target_ratio = target_ratios[category]
                # Calculate the error as the absolute difference
                error = abs(actual_ratio - target_ratio)
                return error
            else:
                return 0.0  # Unknown category
                
        except Exception as e:
            print(f"Error calculating aspect ratio error: {e}")
            return 0.0
    
    def get_detailed_aspect_ratio_info(self, photo_metadata):
        """Get detailed aspect ratio information for debug display"""
        try:
            # Get the photo's actual aspect ratio
            actual_ratio = photo_metadata.width / photo_metadata.height
            category = photo_metadata.aspect_ratio_category
            
            # Define target ratios for each category
            target_ratios = {
                "square": 1.0,
                "4:3_landscape": 4/3,
                "4:3_vertical": 3/4,
                "16:9_landscape": 16/9,
                "16:9_vertical": 9/16,
                "ultra_wide": 21/9
            }
            
            if category in target_ratios:
                target_ratio = target_ratios[category]
                error = abs(actual_ratio - target_ratio)
                return target_ratio, actual_ratio, error
            else:
                return 0.0, actual_ratio, 0.0  # Unknown category
                
        except Exception as e:
            print(f"Error calculating detailed aspect ratio info: {e}")
            return 0.0, 0.0, 0.0
    
    def calculate_display_crop_error(self, photo_metadata, pane):
        """Calculate how much the photo is cropped when displayed in the pane"""
        try:
            # Get the photo's actual aspect ratio
            photo_ratio = photo_metadata.width / photo_metadata.height
            
            # Get the pane's display aspect ratio
            pane_ratio = pane.width / pane.height
            
            # Calculate the actual crop percentage
            # When photo is stretched to fill pane, we need to determine which dimension
            # gets cropped and by how much
            
            if photo_ratio > pane_ratio:
                # Photo is wider than pane - will be cropped horizontally
                # The photo will be scaled to fit the pane height, then cropped horizontally
                scale_factor = pane.height / photo_metadata.height
                scaled_width = photo_metadata.width * scale_factor
                cropped_width = scaled_width - pane.width
                crop_percentage = cropped_width / scaled_width
            else:
                # Photo is taller than pane - will be cropped vertically
                # The photo will be scaled to fit the pane width, then cropped vertically
                scale_factor = pane.width / photo_metadata.width
                scaled_height = photo_metadata.height * scale_factor
                cropped_height = scaled_height - pane.height
                crop_percentage = cropped_height / scaled_height
            
            return max(0.0, crop_percentage)
            
        except Exception as e:
            print(f"Error calculating display crop error: {e}")
            return 0.0
    
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
            
            # Get detailed aspect ratio information
            target_ratio, actual_ratio, aspect_ratio_error = self.get_detailed_aspect_ratio_info(photo_metadata)
            
            # Calculate display crop/letterbox error using actual pane dimensions
            display_crop_error = self.calculate_display_crop_error(photo_metadata, pane)
            
            # Determine display method for debug info
            is_ultra_wide = photo_metadata.aspect_ratio_category == "ultra_wide"
            display_method = "Display Letterbox" if is_ultra_wide else "Display Crop"
            
            # Prepare debug text
            debug_lines = [
                f"Pane: {pane.name}",
                f"File: {os.path.basename(photo_metadata.filepath)}",
                f"Category: {photo_metadata.aspect_ratio_category}",
                f"Original: {photo_metadata.width}x{photo_metadata.height}",
                f"Display: {pane.width}x{pane.height}",
                f"Category Error: {target_ratio:.3f} - {actual_ratio:.3f} = {aspect_ratio_error:.3f}",
                f"{display_method}: {display_crop_error:.4f}",
                f"Date: {photo_metadata.get_formatted_date()}"
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
    
    def start_issue_reporting(self):
        """Start collecting issue description text from user"""
        from datetime import datetime
        
        if not self.is_collecting_issue_text:
            # First Left Control press - start issue reporting
            self.is_collecting_issue_text = True
            self.issue_text_buffer = ""
            self.issue_start_time = datetime.now()
            
            # Store the original debug overlay state to restore later
            self.original_debug_overlay_state = self.debug_overlay_visible
            
            # Automatically show debug overlay if it was hidden
            if not self.debug_overlay_visible:
                self.debug_overlay_visible = True
                print("🔍 Debug overlay automatically enabled for issue reporting")
            
            # Pause the photo rotation timer
            if self.layout_rotation_timer:
                self.root.after_cancel(self.layout_rotation_timer)
                self.layout_rotation_timer = None
                print("⏸️  Photo rotation timer paused for issue reporting")
            
            current_layout = self.layout_manager.get_current_layout()
            layout_name = current_layout.name if current_layout else "Unknown"
            
            print("=" * 80)
            print(f"🚩 ISSUE REPORTING STARTED - {self.issue_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            print(f"   Current Layout: {layout_name}")
            print(f"   Debug Overlay: VISIBLE (auto-enabled for issue reporting)")
            print(f"   Original Debug State: {'VISIBLE' if self.original_debug_overlay_state else 'HIDDEN'}")
            print("   Type your issue description, then press LEFT CONTROL to finish")
            print("   (Timer is paused - photos won't change while typing)")
            print("=" * 80)
            
            # Refresh the display to show debug overlay
            self.refresh_display()
        else:
            # Second Left Control press - finish issue reporting
            self.finish_issue_reporting()
    
    def handle_issue_text_input(self, event):
        """Handle text input while collecting issue description"""
        if event.keysym == 'Control_L':
            # Left Control key pressed again - finish issue reporting
            self.finish_issue_reporting()
        elif event.keysym == 'BackSpace':
            # Handle backspace
            if self.issue_text_buffer:
                self.issue_text_buffer = self.issue_text_buffer[:-1]
                print(f"\r   Issue text: {self.issue_text_buffer}", end="", flush=True)
        elif event.keysym == 'Return':
            # Handle Enter key - add newline to text
            self.issue_text_buffer += "\n"
            print(f"\n   Issue text: {self.issue_text_buffer}", end="", flush=True)
        elif event.keysym == 'Escape':
            # Cancel issue reporting
            self.cancel_issue_reporting()
        elif len(event.keysym) == 1:
            # Regular character input
            self.issue_text_buffer += event.char
            print(f"\r   Issue text: {self.issue_text_buffer}", end="", flush=True)
    
    def finish_issue_reporting(self):
        """Finish collecting issue description and resume normal operation"""
        from datetime import datetime
        
        if not self.is_collecting_issue_text:
            return
        
        end_time = datetime.now()
        duration = (end_time - self.issue_start_time).total_seconds()
        
        # Log the complete issue report
        print("\n" + "=" * 80)
        print(f"🚩 ISSUE REPORT COMPLETED - {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Issue Description:")
        if self.issue_text_buffer.strip():
            # Split by lines and indent each line
            lines = self.issue_text_buffer.strip().split('\n')
            for line in lines:
                print(f"     {line}")
        else:
            print("     (No description provided)")
        print("=" * 80)
        
        # Restore original debug overlay state
        if hasattr(self, 'original_debug_overlay_state'):
            if self.debug_overlay_visible != self.original_debug_overlay_state:
                self.debug_overlay_visible = self.original_debug_overlay_state
                print(f"🔍 Debug overlay restored to {'VISIBLE' if self.original_debug_overlay_state else 'HIDDEN'} (original state)")
                # Refresh the display to show/hide debug overlay
                self.refresh_display()
        
        # Reset issue reporting state
        self.is_collecting_issue_text = False
        self.issue_text_buffer = ""
        self.issue_start_time = None
        
        # Resume the photo rotation timer
        rotation_interval = self.config_manager.get_change_interval()
        self.layout_rotation_timer = self.root.after(rotation_interval, self.rotate_layout_and_photos)
        print(f"▶️  Photo rotation timer resumed - next change in {rotation_interval/1000:.1f} seconds")
    
    def cancel_issue_reporting(self):
        """Cancel issue reporting and resume normal operation"""
        if not self.is_collecting_issue_text:
            return
        
        print("\n❌ Issue reporting cancelled")
        
        # Restore original debug overlay state
        if hasattr(self, 'original_debug_overlay_state'):
            if self.debug_overlay_visible != self.original_debug_overlay_state:
                self.debug_overlay_visible = self.original_debug_overlay_state
                print(f"🔍 Debug overlay restored to {'VISIBLE' if self.original_debug_overlay_state else 'HIDDEN'} (original state)")
                # Refresh the display to show/hide debug overlay
                self.refresh_display()
        
        # Reset issue reporting state
        self.is_collecting_issue_text = False
        self.issue_text_buffer = ""
        self.issue_start_time = None
        
        # Resume the photo rotation timer
        rotation_interval = self.config_manager.get_change_interval()
        self.layout_rotation_timer = self.root.after(rotation_interval, self.rotate_layout_and_photos)
        print(f"▶️  Photo rotation timer resumed - next change in {rotation_interval/1000:.1f} seconds")
    
    def add_debug_marker(self):
        """Add a timestamp marker to the console log for issue reporting (legacy method)"""
        from datetime import datetime
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds
        current_layout = self.layout_manager.get_current_layout()
        layout_name = current_layout.name if current_layout else "Unknown"
        
        print("=" * 80)
        print(f"🚩 USER ISSUE MARKER - {current_time}")
        print(f"   Current Layout: {layout_name}")
        if self.debug_overlay_visible:
            print(f"   Debug Overlay: VISIBLE")
        else:
            print(f"   Debug Overlay: HIDDEN")
        print("   Press spacebar again to add another marker")
        print("=" * 80)
    
    def next_photos(self):
        """Move to the next set of photos (legacy method - kept for debug mode Enter key)"""
        if not self.running:
            return
        
        # In the new system, this triggers a combined layout+photo rotation
        print("🔄 Manual trigger of combined rotation")
        
        # Trigger combined rotation immediately
        self.rotate_layout_and_photos()
    
    def on_key_press(self, event):
        """Handle key press events"""
        if self.is_collecting_issue_text:
            # We're collecting issue text - handle text input
            self.handle_issue_text_input(event)
        elif event.keysym == 'v' or event.keysym == 'V':
            # Toggle debug overlay visibility
            self.debug_overlay_visible = not self.debug_overlay_visible
            print(f"🔍 Debug overlay {'enabled' if self.debug_overlay_visible else 'disabled'}")
            # Refresh the display to show/hide debug overlay
            self.refresh_display()
        elif event.keysym == 'Return':
            # Enter key advances to next layout
            print("🔄 Manual advancement to next layout...")
            self.next_photos()
        elif event.keysym == 'Control_L':
            # Left Control key starts issue reporting mode
            self.start_issue_reporting()
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
        
        print("🔄 Shutting down screensaver...")
        self.root.quit()
    
    def run(self):
        """Start the screen saver"""
        try:
            # Ensure window is brought to foreground before starting main loop
            print("🚀 Starting screensaver main loop...")
            self.root.update()  # Process any pending events to ensure window is fully initialized
            self._bring_to_foreground()  # Bring to foreground again after window is fully ready
            self.root.mainloop()
        except KeyboardInterrupt:
            print("⌨️  Keyboard interrupt received")
            self.exit_screensaver()
        except Exception as e:
            print(f"❌ Unexpected error in screensaver: {e}")
            self.exit_screensaver()
