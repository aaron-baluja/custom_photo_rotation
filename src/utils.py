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
                                photo_width: int, photo_height: int, 
                                stretch_to_fill: bool = True) -> Tuple[int, int]:
    """Calculate display dimensions for a photo on screen
    
    Args:
        screen_width: Width of the target display area
        screen_height: Height of the target display area  
        photo_width: Original width of the photo
        photo_height: Original height of the photo
        stretch_to_fill: If True, stretch photo to fill entire area (may distort)
                       If False, maintain aspect ratio (may leave empty space)
    
    Returns:
        Tuple of (target_width, target_height) for display
    """
    if photo_height == 0:
        return screen_width, screen_height
    
    if stretch_to_fill:
        # Stretch photo to completely fill the pane dimensions
        # This will distort the photo but ensure no empty space
        return screen_width, screen_height
    else:
        # Maintain aspect ratio (original behavior)
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


def calculate_crop_dimensions(screen_width: int, screen_height: int,
                             photo_width: int, photo_height: int) -> Tuple[int, int, int, int]:
    """Calculate dimensions for cropping a photo to fit a pane while maintaining aspect ratio
    
    Args:
        screen_width: Width of the target display area
        screen_height: Height of the target display area
        photo_width: Original width of the photo
        photo_height: Original height of the photo
    
    Returns:
        Tuple of (crop_x, crop_y, crop_width, crop_height) for cropping the original photo
    """
    if photo_height == 0:
        return 0, 0, photo_width, photo_height
    
    # Calculate the scaling factor to fit the photo within the pane
    # while maintaining aspect ratio
    scale_x = screen_width / photo_width
    scale_y = screen_height / photo_height
    
    # Use the larger scale to ensure the photo covers the entire pane
    scale = max(scale_x, scale_y)
    
    # Calculate the scaled dimensions
    scaled_width = int(photo_width * scale)
    scaled_height = int(photo_height * scale)
    
    # Calculate the crop area to center the photo in the pane
    crop_x = (scaled_width - screen_width) // 2
    crop_y = (scaled_height - screen_height) // 2
    
    # Ensure crop coordinates are within bounds
    crop_x = max(0, crop_x)
    crop_y = max(0, crop_y)
    crop_width = min(screen_width, scaled_width - crop_x)
    crop_height = min(screen_height, scaled_height - crop_y)
    
    return crop_x, crop_y, crop_width, crop_height


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
