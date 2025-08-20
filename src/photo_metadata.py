"""
Photo metadata extraction and storage module.
"""

import os
from datetime import datetime
from PIL import Image


class PhotoMetadata:
    """Extracts and stores photo metadata"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.width = 0
        self.height = 0
        self.date_taken = None
        self.aspect_ratio_category = None
        self.file_size = 0
        self.extract_metadata()
    
    def extract_metadata(self):
        """Extract metadata from photo file"""
        try:
            # Get file size
            self.file_size = os.path.getsize(self.filepath)
            
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
    
    def get_aspect_ratio(self):
        """Get the aspect ratio as a float"""
        if self.height == 0:
            return 0.0
        return self.width / self.height
    
    def get_formatted_date(self):
        """Get date taken in a readable format"""
        if self.date_taken:
            return self.date_taken.strftime('%Y-%m-%d %H:%M:%S')
        return "Unknown"
    
    def get_file_size_mb(self):
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)
    
    def __str__(self):
        return f"{self.filename} ({self.width}x{self.height}) - {self.aspect_ratio_category}"
    
    def __repr__(self):
        return f"PhotoMetadata(filepath='{self.filepath}', width={self.width}, height={self.height})"
