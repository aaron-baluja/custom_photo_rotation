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
        
        layout = self.layout_manager.get_current_layout()
        
        # Special handling for dual pane layout
        if layout.type.value == "dual_pane" and len(layout.panes) == 2:
            return self._get_dual_pane_photos()
        
        # Default behavior for other layouts
        return self._get_default_pane_photos()
    
    def _get_dual_pane_photos(self) -> Dict[str, PhotoMetadata]:
        """Special photo selection for dual pane: one square and one 4:3 vertical"""
        layout = self.layout_manager.get_current_layout()
        pane_photos = {}
        
        print(f"🔍 Selecting dual pane photos (one square + one 4:3 vertical)...")
        
        # Get all available photos by category
        all_photos_by_category = {}
        for pane in layout.panes:
            if not self.has_photos_for_pane(pane.name):
                continue
            
            photos = self.pane_photos[pane.name]
            for photo in photos:
                category = photo.aspect_ratio_category
                if category not in all_photos_by_category:
                    all_photos_by_category[category] = []
                all_photos_by_category[category].append(photo)
        
        # Remove duplicates within each category
        for category in all_photos_by_category:
            unique_photos = []
            seen_paths = set()
            for photo in all_photos_by_category[category]:
                if photo.filepath not in seen_paths:
                    unique_photos.append(photo)
                    seen_paths.add(photo.filepath)
            all_photos_by_category[category] = unique_photos
        
        # Select one square photo and one 4:3 vertical photo
        group_square = []
        group_43_vertical = []
        
        for category, photos in all_photos_by_category.items():
            if category == "square":
                group_square.extend(photos)
            elif category == "4:3_vertical":
                group_43_vertical.extend(photos)
        
        print(f"  📊 Available: {len(group_square)} square photos, {len(group_43_vertical)} 4:3 vertical photos")
        
        if not group_square or not group_43_vertical:
            print(f"  ⚠️  Cannot create dual pane layout: missing photo types")
            print(f"      Square photos: {len(group_square)}")
            print(f"      4:3 vertical photos: {len(group_43_vertical)}")
            return self._get_default_pane_photos()
        
        # Select photos (using current indices to maintain rotation)
        photo_square = group_square[self.pane_photo_indices.get("dual_square", 0) % len(group_square)]
        photo_43_vertical = group_43_vertical[self.pane_photo_indices.get("dual_43_vertical", 0) % len(group_43_vertical)]
        
        # Randomly assign to left/right panes
        import random
        panes = list(layout.panes)
        random.shuffle(panes)
        
        pane_photos[panes[0].name] = photo_square
        pane_photos[panes[1].name] = photo_43_vertical
        
        # Update indices for next rotation
        self.pane_photo_indices["dual_square"] = (self.pane_photo_indices.get("dual_square", 0) + 1) % len(group_square)
        self.pane_photo_indices["dual_43_vertical"] = (self.pane_photo_indices.get("dual_43_vertical", 0) + 1) % len(group_43_vertical)
        
        print(f"  ✅ Selected square photo: {photo_square.filepath} → {panes[0].name} pane")
        print(f"  ✅ Selected 4:3 vertical photo: {photo_43_vertical.filepath} → {panes[1].name} pane")
        
        return pane_photos
    
    def _get_default_pane_photos(self) -> Dict[str, PhotoMetadata]:
        """Default photo selection for non-dual pane layouts"""
        layout = self.layout_manager.get_current_layout()
        pane_photos = {}
        used_photos = set()
        
        print(f"🔍 Selecting unique photos for {len(layout.panes)} panes...")
        
        for pane in layout.panes:
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
