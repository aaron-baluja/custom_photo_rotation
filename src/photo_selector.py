"""
Photo selection module for different layout panes.
"""

from typing import Dict, List, Optional, Tuple
from photo_metadata import PhotoMetadata
from layout_manager import LayoutManager
import random


class PhotoSelector:
    """Selects appropriate photos for each pane based on layout requirements"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager
        self.pane_photo_indices = {}  # Track current photo index for each pane
        self.pane_photos = {}  # Store photos organized by pane
        self.used_photos = set()  # Track photos currently in use across all panes
    
    def organize_photos_by_pane(self, photos_by_category: Dict[str, List[PhotoMetadata]]) -> Dict[str, List[PhotoMetadata]]:
        """Organize photos by pane based on current layout"""
        if not self.layout_manager.get_current_layout():
            return {}
        
        pane_photos = {}
        
        for pane in self.layout_manager.get_current_layout().panes:
            pane_photos[pane.name] = []
            
            # Collect photos that match this pane's category requirements
            for category in pane.photo_categories:
                if category in photos_by_category:
                    pane_photos[pane.name].extend(photos_by_category[category])
            
            # Remove duplicates within the pane
            unique_photos = []
            seen_photos = set()
            for photo in pane_photos[pane.name]:
                if photo.filepath not in seen_photos:
                    unique_photos.append(photo)
                    seen_photos.add(photo.filepath)
            pane_photos[pane.name] = unique_photos
            
            # Initialize photo index for this pane
            self.pane_photo_indices[pane.name] = 0
        
        self.pane_photos = pane_photos
        self.used_photos.clear()  # Reset used photos tracking
        return pane_photos
    
    def get_next_photo_for_pane(self, pane_name: str) -> Optional[PhotoMetadata]:
        """Get the next photo for a specific pane, ensuring uniqueness across panes"""
        if pane_name not in self.pane_photos or not self.pane_photos[pane_name]:
            return None
        
        photos = self.pane_photos[pane_name]
        current_index = self.pane_photo_indices[pane_name]
        
        # Try to find a photo that's not currently used by other panes
        attempts = 0
        max_attempts = len(photos) * 2  # Prevent infinite loops
        
        while attempts < max_attempts:
            # Get current photo
            photo = photos[current_index]
            
            # Check if this photo is already being used by another pane
            if photo.filepath not in self.used_photos:
                # Mark this photo as used
                self.used_photos.add(photo.filepath)
                
                # Move to next photo (circular)
                self.pane_photo_indices[pane_name] = (current_index + 1) % len(photos)
                
                return photo
            
            # Move to next photo and try again
            current_index = (current_index + 1) % len(photos)
            attempts += 1
        
        # If we can't find a unique photo, just return the current one
        # and mark it as used to prevent immediate duplication
        photo = photos[current_index]
        self.used_photos.add(photo.filepath)
        self.pane_photo_indices[pane_name] = (current_index + 1) % len(photos)
        
        return photo
    
    def get_photo_count_for_pane(self, pane_name: str) -> int:
        """Get the total number of photos available for a pane"""
        if pane_name not in self.pane_photos:
            return 0
        return len(self.pane_photos[pane_name])
    
    def get_pane_summary(self) -> Dict[str, Dict]:
        """Get a summary of photos available for each pane"""
        summary = {}
        
        for pane_name, photos in self.pane_photos.items():
            summary[pane_name] = {
                'total_photos': len(photos),
                'categories': self.layout_manager.get_photo_categories_for_pane(pane_name),
                'dimensions': self.layout_manager.get_pane_dimensions(pane_name)
            }
        
        return summary
    
    def reset_pane_indices(self):
        """Reset photo indices for all panes"""
        for pane_name in self.pane_photo_indices:
            self.pane_photo_indices[pane_name] = 0
        self.used_photos.clear()  # Reset used photos tracking
    
    def get_pane_photo_categories(self, pane_name: str) -> List[str]:
        """Get the photo categories that can be displayed in a specific pane"""
        return self.layout_manager.get_photo_categories_for_pane(pane_name)
    
    def has_photos_for_pane(self, pane_name: str) -> bool:
        """Check if a pane has any photos available"""
        return pane_name in self.pane_photos and len(self.pane_photos[pane_name]) > 0
    
    def get_all_pane_names(self) -> List[str]:
        """Get all pane names from the current layout"""
        if not self.layout_manager.get_current_layout():
            return []
        
        return [pane.name for pane in self.layout_manager.get_current_layout().panes]
    
    def get_unique_photos_for_all_panes(self) -> Dict[str, PhotoMetadata]:
        """Get unique photos for all panes simultaneously, ensuring no duplicates"""
        if not self.layout_manager.get_current_layout():
            return {}
        
        pane_photos = {}
        used_photos = set()
        
        print(f"🔍 Selecting unique photos for {len(self.layout_manager.get_current_layout().panes)} panes...")
        
        for pane in self.layout_manager.get_current_layout().panes:
            if not self.has_photos_for_pane(pane.name):
                print(f"  ⚠️  No photos available for {pane.name} pane")
                continue
            
            photos = self.pane_photos[pane.name]
            current_index = self.pane_photo_indices[pane.name]
            
            print(f"  📱 {pane.name.capitalize()} pane: {len(photos)} photos available, starting from index {current_index}")
            
            # Try to find a unique photo for this pane
            attempts = 0
            max_attempts = len(photos) * 2
            
            while attempts < max_attempts:
                photo = photos[current_index]
                
                if photo.filepath not in used_photos:
                    # Found a unique photo
                    pane_photos[pane.name] = photo
                    used_photos.add(photo.filepath)
                    
                    print(f"    ✅ Selected unique photo: {photo.filepath} (category: {photo.aspect_ratio_category})")
                    
                    # Update the index for next time
                    self.pane_photo_indices[pane.name] = (current_index + 1) % len(photos)
                    break
                
                current_index = (current_index + 1) % len(photos)
                attempts += 1
            
            # If we couldn't find a unique photo, use the current one anyway
            if pane.name not in pane_photos:
                photo = photos[current_index]
                pane_photos[pane.name] = photo
                used_photos.add(photo.filepath)
                self.pane_photo_indices[pane.name] = (current_index + 1) % len(photos)
                
                print(f"    ⚠️  Using duplicate photo after {attempts} attempts: {photo.filepath} (category: {photo.aspect_ratio_category})")
        
        print(f"🎯 Final photo selection: {len(pane_photos)} panes filled")
        for pane_name, photo in pane_photos.items():
            print(f"  {pane_name}: {photo.aspect_ratio_category} photo")
        
        return pane_photos
