import tkinter as tk
import os
import time
from PIL import Image, ImageTk
import threading

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
        
        # Variables
        self.image_folder = ""
        self.images = []
        self.current_image_index = 0
        self.photo = None
        self.running = False
        
        # Load config and start
        self.load_config()
        if self.image_folder:
            self.load_images()
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
    
    def load_images(self):
        """Load all supported image files from the configured folder"""
        if not self.image_folder:
            return
            
        self.images = []
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        
        try:
            if not os.path.exists(self.image_folder):
                self.show_error(f"Image folder not found: {self.image_folder}\nPlease check config.txt file.")
                return
                
            for filename in os.listdir(self.image_folder):
                if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                    filepath = os.path.join(self.image_folder, filename)
                    self.images.append(filepath)
            
            if self.images:
                self.start_slideshow()
            else:
                self.show_error(f"No supported images found in: {self.image_folder}\nSupported formats: JPG, PNG, BMP, GIF, TIFF")
                
        except Exception as e:
            self.show_error(f"Error loading images: {str(e)}")
    
    def start_slideshow(self):
        """Start the image slideshow"""
        if not self.images:
            return
            
        self.running = True
        self.show_next_image()
    
    def show_next_image(self):
        """Display the next image in the slideshow"""
        if not self.running or not self.images:
            return
            
        try:
            # Load and display current image
            image_path = self.images[self.current_image_index]
            image = Image.open(image_path)
            
            # Resize image to fit screen while maintaining 16:9 aspect ratio
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Calculate target dimensions for 16:9 aspect ratio
            target_ratio = 16 / 9
            if screen_width / screen_height > target_ratio:
                # Screen is wider than 16:9, fit to height
                target_height = screen_height
                target_width = int(target_height * target_ratio)
            else:
                # Screen is taller than 16:9, fit to width
                target_width = screen_width
                target_height = int(target_width / target_ratio)
            
            # Resize image
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(image)
            
            # Create and configure image label
            self.image_label = tk.Label(self.root, image=self.photo, bg='black')
            self.image_label.pack(expand=True, fill='both')
            
            # Schedule next image
            self.root.after(15000, self.next_image)  # 15 seconds
            
        except Exception as e:
            print(f"Error displaying image: {e}")
            self.next_image()
    
    def next_image(self):
        """Move to the next image"""
        if not self.running:
            return
            
        # Remove current image
        if hasattr(self, 'image_label'):
            self.image_label.destroy()
            
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.show_next_image()
    
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
