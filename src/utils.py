"""
Utility functions for the screen saver application.
"""

import os
from typing import List, Tuple


def get_supported_formats() -> set:
    """Get set of supported image file extensions"""
    return {'.jpg', '.jpeg', '.png'}


def is_image_file(filename: str) -> bool:
    """Check if a filename has a supported image extension"""
    return any(filename.lower().endswith(fmt) for fmt in get_supported_formats())


def find_image_files(folder_path: str) -> List[str]:
    """Recursively find all image files in a folder and subdirectories"""
    image_files = []
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if is_image_file(filename):
                    filepath = os.path.join(root, filename)
                    image_files.append(filepath)
    except Exception as e:
        print(f"Error searching for images in {folder_path}: {e}")
    
    return image_files


def calculate_display_dimensions(screen_width: int, screen_height: int, 
                                photo_width: int, photo_height: int) -> Tuple[int, int]:
    """Calculate optimal display dimensions for a photo on screen"""
    if photo_height == 0:
        return screen_width, screen_height
    
    photo_ratio = photo_width / photo_height
    screen_ratio = screen_width / screen_height
    
    if screen_ratio > photo_ratio:
        # Screen is wider than photo, fit to height
        target_height = screen_height
        target_width = int(target_height * photo_ratio)
    else:
        # Screen is taller than photo, fit to width
        target_width = screen_width
        target_height = int(target_width / photo_ratio)
    
    return target_width, target_height


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def safe_filename(filename: str) -> str:
    """Convert filename to safe string for display"""
    # Remove or replace problematic characters
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- "
    return ''.join(c for c in filename if c in safe_chars)


def get_folder_name(path: str) -> str:
    """Get the name of the folder from a path"""
    return os.path.basename(os.path.normpath(path))


def print_separator(char: str = "=", length: int = 50):
    """Print a separator line for console output"""
    print(char * length)
