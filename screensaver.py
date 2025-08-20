import tkinter as tk
import os
import time
from PIL import Image, ImageTk
import threading
from datetime import datetime
import math

class PhotoClassifier:
    """Classifies photos based on aspect ratio and metadata"""
    
    def __init__(self):
        # Define target aspect ratios with tolerance
        self.aspect_ratios = {
            'ultra_wide': {'width': 21, 'height': 9, 'tolerance': 0.3},  # 2.33 ratio for ultra-wide/panoramic
            '16:9_landscape': {'width': 16, 'height': 9, 'tolerance': 0.25},
            '16:9_vertical': {'width': 9, 'height': 16, 'tolerance': 0.2},
            '4:3_landscape': {'width': 4, 'height': 3, 'tolerance': 0.2},
            '4:3_vertical': {'width': 3, 'height': 4, 'tolerance': 0.2},
            'square': {'width': 1, 'height': 1, 'tolerance': 0.2}
        }
    
    def classify_photo(self, width, height):
        """Classify a photo based on its dimensions"""
        if width == 0 or height == 0:
            return 'unknown'
        
        actual_ratio = width / height
        best_match = None
        min_difference = float('inf')
        
        for category, specs in self.aspect_ratios.items():
            target_ratio = specs['width'] / specs['height']
            difference = abs(actual_ratio - target_ratio)
            
            if difference < min_difference:
                min_difference = difference
                best_match = category
        
        # Check if the best match is within tolerance
        if best_match and min_difference <= self.aspect_ratios[best_match]['tolerance']:
            return best_match
        
        # Photo doesn't match any category within tolerance
        
        return 'unknown'
    
    def get_category_display_name(self, category):
        """Get human-readable name for category"""
        display_names = {
            'ultra_wide': 'Ultra-Wide/Panoramic',
            '16:9_landscape': '16:9 Landscape',
            '16:9_vertical': '16:9 Vertical',
            '4:3_landscape': '4:3 Landscape',
            '4:3_vertical': '4:3 Vertical',
            'square': 'Square',
            'unknown': 'Unknown'
        }
        return display_names.get(category, category)

class PhotoMetadata:
    """Extracts and stores photo metadata"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.width = 0
        self.height = 0
        self.date_taken = None
        self.aspect_ratio_category = None
        self.extract_metadata()
    
    def extract_metadata(self):
        """Extract metadata from photo file"""
        try:
            with Image.open(self.filepath) as img:
                self.width, self.height = img.size
                
                # Try to extract EXIF date taken
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    # EXIF tag 36867 is DateTimeOriginal (date taken)
                    if 36867 in exif:
                        try:
                            date_str = exif[36867]
                            self.date_taken = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                        except ValueError:
                            pass
                
                # If no EXIF date, use file modification time
                if not self.date_taken:
                    file_time = os.path.getmtime(self.filepath)
                    self.date_taken = datetime.fromtimestamp(file_time)
                
        except Exception as e:
            print(f"Error extracting metadata from {self.filepath}: {e}")
    
    def __str__(self):
        return f"{self.filename} ({self.width}x{self.height}) - {self.aspect_ratio_category}"

class ScreenSaver:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Custom Photo Rotation Screen Saver")
        
        # Configure fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        # Bind escape key to exit
        self.root.bind('<Escape>', lambda e: self.exit_screensaver())
        self.root.bind('<Button-1>', lambda e: self.exit_screensaver())
        self.root.bind('<Key>', lambda e: self.exit_screensaver())
        
        # Initialize components
        self.photo_classifier = PhotoClassifier()
        
        # Variables
        self.image_folder = ""
        self.photos_by_category = {}
        self.current_category = None
        self.current_photo_index = 0
        self.photo = None
        self.running = False
        
        # Load config and start
        self.load_config()
        if self.image_folder:
            self.load_and_classify_photos()
        else:
            self.show_error("No image folder configured. Please check config.txt file.")
    
    def load_config(self):
        """Load image folder path from config file"""
        config_file = "config.txt"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('IMAGE_FOLDER='):
                            self.image_folder = line.split('=', 1)[1].strip()
                            # Remove quotes if present
                            if (self.image_folder.startswith('"') and self.image_folder.endswith('"')) or \
                               (self.image_folder.startswith("'") and self.image_folder.endswith("'")):
                                self.image_folder = self.image_folder[1:-1]
                            break
            else:
                # Create default config if it doesn't exist
                default_folder = os.path.expanduser("~/Pictures/Screensaver")
                with open(config_file, 'w') as f:
                    f.write(f"# Screen Saver Configuration\n")
                    f.write(f"# Path to the folder containing your images\n")
                    f.write(f"IMAGE_FOLDER={default_folder}\n")
                self.image_folder = default_folder
                
        except Exception as e:
            print(f"Error loading config: {e}")
            self.image_folder = ""
    
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
    
    def load_and_classify_photos(self):
        """Load, classify, and organize photos by aspect ratio category"""
        if not self.image_folder:
            return
            
        self.photos_by_category = {}
        supported_formats = {'.jpg', '.jpeg', '.png'}
        
        try:
            if not os.path.exists(self.image_folder):
                self.show_error(f"Image folder not found: {self.image_folder}\nPlease check config.txt file.")
                return
            
            print(f"Loading and classifying photos from: {self.image_folder}")
            
            # Recursively search for images in the folder and all subdirectories
            for root, dirs, files in os.walk(self.image_folder):
                for filename in files:
                    if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                        filepath = os.path.join(root, filename)
                        photo_metadata = PhotoMetadata(filepath)
                        
                        # Classify the photo
                        category = self.photo_classifier.classify_photo(photo_metadata.width, photo_metadata.height)
                        photo_metadata.aspect_ratio_category = category
                        
                        # Organize by category
                        if category not in self.photos_by_category:
                            self.photos_by_category[category] = []
                        self.photos_by_category[category].append(photo_metadata)
            
            # Print classification summary
            total_photos = sum(len(photos) for photos in self.photos_by_category.values())
            print(f"\nPhoto Classification Summary:")
            print(f"Total photos found: {total_photos}")
            
            for category, photos in self.photos_by_category.items():
                display_name = self.photo_classifier.get_category_display_name(category)
                print(f"  {display_name}: {len(photos)} photos")
            
            if total_photos > 0:
                self.start_slideshow()
            else:
                self.show_error(f"No supported images found in: {self.image_folder}\nSupported formats: JPG, JPEG, PNG")
                
        except Exception as e:
            self.show_error(f"Error loading images: {str(e)}")
    
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
            
            # Resize image to fit screen while maintaining aspect ratio
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calculate target dimensions for the photo's aspect ratio
            photo_ratio = photo_metadata.width / photo_metadata.height
            if screen_width / screen_height > photo_ratio:
                # Screen is wider than photo, fit to height
                target_height = screen_height
                target_width = int(target_height * photo_ratio)
            else:
                # Screen is taller than photo, fit to width
                target_width = screen_width
                target_height = int(target_width / photo_ratio)
            
            # Resize image
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(image)
            
            # Create and configure image label
            self.image_label = tk.Label(self.root, image=self.photo, bg='black')
            self.image_label.pack(expand=True, fill='both')
            
            # Schedule next photo
            self.root.after(15000, self.next_photo)  # 15 seconds
            
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

if __name__ == "__main__":
    app = ScreenSaver()
    app.run()
