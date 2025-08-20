"""
Main screen saver application module.
"""

import tkinter as tk
from PIL import Image, ImageTk
import os

from photo_classifier import PhotoClassifier
from photo_metadata import PhotoMetadata
from config_manager import ConfigManager
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
        self.root.bind('<Key>', lambda e: self.exit_screensaver())
        
        # Variables
        self.photos_by_category = {}
        self.current_category = None
        self.current_photo_index = 0
        self.photo = None
        self.running = False
        
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
        
        # Start slideshow if photos found
        total_photos = sum(len(photos) for photos in self.photos_by_category.values())
        if total_photos > 0:
            self.start_slideshow()
        else:
            self.show_error(f"No supported images found in: {image_folder}")
    
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
        if not self.photos_by_category:
            return
            
        self.running = True
        
        # Start with the first available category
        available_categories = [cat for cat in self.photos_by_category.keys() if self.photos_by_category[cat]]
        if available_categories:
            self.current_category = available_categories[0]
            self.current_photo_index = 0
            self.show_next_photo()
    
    def show_next_photo(self):
        """Display the next photo in the slideshow"""
        if not self.running or not self.photos_by_category:
            return
            
        try:
            # Get current photo
            current_photos = self.photos_by_category[self.current_category]
            if not current_photos:
                self.move_to_next_category()
                return
            
            photo_metadata = current_photos[self.current_photo_index]
            
            # Load and display image
            image = Image.open(photo_metadata.filepath)
            
            # Calculate display dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            target_width, target_height = calculate_display_dimensions(
                screen_width, screen_height,
                photo_metadata.width, photo_metadata.height
            )
            
            # Resize image
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(image)
            
            # Create and configure image label
            self.image_label = tk.Label(self.root, image=self.photo, bg='black')
            self.image_label.pack(expand=True, fill='both')
            
            # Schedule next photo
            display_interval = self.config_manager.get_display_interval()
            self.root.after(display_interval, self.next_photo)
            
        except Exception as e:
            print(f"Error displaying photo: {e}")
            self.next_photo()
    
    def next_photo(self):
        """Move to the next photo"""
        if not self.running:
            return
            
        # Remove current image
        if hasattr(self, 'image_label'):
            self.image_label.destroy()
            
        # Move to next photo in current category
        current_photos = self.photos_by_category[self.current_category]
        self.current_photo_index = (self.current_photo_index + 1) % len(current_photos)
        
        # If we've completed a category, move to the next one
        if self.current_photo_index == 0:
            self.move_to_next_category()
        
        self.show_next_photo()
    
    def move_to_next_category(self):
        """Move to the next category with photos"""
        available_categories = [cat for cat in self.photos_by_category.keys() if self.photos_by_category[cat]]
        if not available_categories:
            return
            
        current_index = available_categories.index(self.current_category)
        next_index = (current_index + 1) % len(available_categories)
        self.current_category = available_categories[next_index]
        self.current_photo_index = 0
        
        # Print category transition
        display_name = self.photo_classifier.get_category_display_name(self.current_category)
        photo_count = len(self.photos_by_category[self.current_category])
        print(f"Switching to category: {display_name} ({photo_count} photos)")
    
    def exit_screensaver(self):
        """Exit the screen saver"""
        self.running = False
        self.root.quit()
    
    def run(self):
        """Start the screen saver"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.exit_screensaver()
