"""
Photo selection module for different layout panes.
"""

from typing import Dict, List, Optional, Tuple
from photo_metadata import PhotoMetadata
from layout_manager import LayoutManager
import random
import os
from datetime import datetime, timedelta


class PhotoSelector:
    """Selects appropriate photos for each pane based on layout requirements"""
    
    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager
        self.pane_photo_indices = {}  # Track current photo index for each pane
        self.pane_photos = {}  # Store photos organized by pane
        self.used_photos = set()  # Track photos currently in use across all panes
        
        # New selection criteria tracking
        self.category_used_photos = {}  # Track used photos per category for repetition reduction
        self.category_available_photos = {}  # Track available photos per category
        self.time_weighted_photos = set()  # Photos that should appear 3x more often
    
    def organize_photos_by_pane(self, photos_by_category: Dict[str, List[PhotoMetadata]]) -> Dict[str, List[PhotoMetadata]]:
        """Organize photos by pane based on current layout"""
        if not self.layout_manager.get_current_layout():
            return {}
        
        # Store photos by category for use in selection methods
        self.all_photos_by_category = photos_by_category
        
        # Initialize new selection criteria
        self.calculate_time_weighting(photos_by_category)
        self.initialize_category_tracking(photos_by_category)
        
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
    
    def calculate_crop_value(self, photo: PhotoMetadata, pane) -> float:
        """Calculate the crop value for a photo in a specific pane"""
        try:
            # Get the photo's actual aspect ratio
            photo_ratio = photo.width / photo.height
            
            # Get the pane's display aspect ratio
            pane_ratio = pane.width / pane.height
            
            # Calculate the crop value as the absolute difference
            crop_value = abs(photo_ratio - pane_ratio)
            return crop_value
            
        except Exception as e:
            print(f"Error calculating crop value: {e}")
            return 0.0
    
    def validate_photo_layout(self, pane_photos: Dict[str, PhotoMetadata]) -> bool:
        """Validate that no photo has a crop value exceeding 0.2 (excludes ultra-wide photos)"""
        layout = self.layout_manager.get_current_layout()
        if not layout:
            return False
        
        max_allowed_crop = 0.2
        
        for pane_name, photo in pane_photos.items():
            # Skip validation for ultra-wide photos since they use letterboxing
            if photo.aspect_ratio_category == "ultra_wide":
                continue
            
            # Find the corresponding pane
            pane = None
            for p in layout.panes:
                if p.name == pane_name:
                    pane = p
                    break
            
            if not pane:
                continue
            
            # Calculate crop value for this photo in this pane
            crop_value = self.calculate_crop_value(photo, pane)
            
            if crop_value > max_allowed_crop:
                print(f"  ⚠️  Photo {os.path.basename(photo.filepath)} has crop value {crop_value:.4f} > {max_allowed_crop} in {pane_name} pane")
                return False
        
        return True
    
    def calculate_time_weighting(self, photos_by_category: Dict[str, List[PhotoMetadata]]):
        """Calculate which photos should have increased likelihood based on time of year"""
        current_date = datetime.now()
        current_month_day = (current_date.month, current_date.day)
        
        # Calculate the 7-day window around current date (ignoring year)
        start_date = current_date - timedelta(days=7)
        end_date = current_date + timedelta(days=7)
        
        start_month_day = (start_date.month, start_date.day)
        end_month_day = (end_date.month, end_date.day)
        
        print(f"📅 Time weighting: Looking for photos taken between {start_date.strftime('%B %d')} and {end_date.strftime('%B %d')} (any year)")
        
        self.time_weighted_photos.clear()
        total_time_weighted = 0
        
        for category, photos in photos_by_category.items():
            for photo in photos:
                if self.is_photo_in_time_window(photo, start_month_day, end_month_day, current_month_day):
                    self.time_weighted_photos.add(photo.filepath)
                    total_time_weighted += 1
        
        print(f"📊 Time weighted photos: {total_time_weighted} out of {sum(len(photos) for photos in photos_by_category.values())} total photos")
    
    def is_photo_in_time_window(self, photo: PhotoMetadata, start_month_day: tuple, end_month_day: tuple, current_month_day: tuple) -> bool:
        """Check if a photo was taken within the 7-day window around current date (ignoring year)"""
        if not photo.date_taken:
            return False
        
        try:
            # Extract month and day from photo's date taken
            if isinstance(photo.date_taken, str):
                # Parse the date string
                photo_date = datetime.strptime(photo.date_taken.split()[0], '%Y-%m-%d')
            else:
                photo_date = photo.date_taken
            
            photo_month_day = (photo_date.month, photo_date.day)
            
            # Handle year-end boundary cases
            if start_month_day[0] > end_month_day[0]:  # Crosses year boundary
                # Check if photo is in either the end of previous year or start of next year window
                return (photo_month_day >= start_month_day or photo_month_day <= end_month_day)
            else:
                # Normal case within same year
                return start_month_day <= photo_month_day <= end_month_day
                
        except Exception as e:
            print(f"Error parsing date for {photo.filepath}: {e}")
            return False
    
    def initialize_category_tracking(self, photos_by_category: Dict[str, List[PhotoMetadata]]):
        """Initialize tracking for repetition reduction per category"""
        self.category_used_photos.clear()
        self.category_available_photos.clear()
        
        for category, photos in photos_by_category.items():
            self.category_used_photos[category] = set()
            self.category_available_photos[category] = [photo.filepath for photo in photos]
        
        print(f"🔄 Initialized category tracking:")
        for category, photos in self.category_available_photos.items():
            print(f"  {category}: {len(photos)} photos available")
    
    def get_available_photos_for_category(self, category: str, photos_by_category: Dict[str, List[PhotoMetadata]]) -> List[PhotoMetadata]:
        """Get photos that haven't been used yet in this category, with time weighting applied"""
        if category not in photos_by_category:
            return []
        
        all_photos = photos_by_category[category]
        used_in_category = self.category_used_photos.get(category, set())
        
        # Get photos that haven't been used yet in this category
        available_photos = [photo for photo in all_photos if photo.filepath not in used_in_category]
        
        # If all photos in category have been used, reset the category
        if not available_photos:
            print(f"  🔄 All {category} photos used, resetting category")
            self.category_used_photos[category].clear()
            available_photos = all_photos.copy()
        
        # Apply time weighting: photos in time window appear 3x more often
        weighted_photos = []
        for photo in available_photos:
            if photo.filepath in self.time_weighted_photos:
                # Add time-weighted photos 3 times (3x likelihood)
                weighted_photos.extend([photo, photo, photo])
            else:
                # Add regular photos once
                weighted_photos.append(photo)
        
        return weighted_photos
    
    def mark_photo_as_used(self, photo: PhotoMetadata):
        """Mark a photo as used in its category for repetition reduction"""
        category = photo.aspect_ratio_category
        if category not in self.category_used_photos:
            self.category_used_photos[category] = set()
        
        self.category_used_photos[category].add(photo.filepath)
        
        # Debug info
        total_in_category = len(self.category_available_photos.get(category, []))
        used_in_category = len(self.category_used_photos[category])
        print(f"  📝 Marked {os.path.basename(photo.filepath)} as used in {category} ({used_in_category}/{total_in_category} used)")
    
    def try_alternative_photo_combinations(self, pane_photos: Dict[str, PhotoMetadata], max_attempts: int = 10) -> Dict[str, PhotoMetadata]:
        """Try alternative photo combinations to reduce crop values"""
        layout = self.layout_manager.get_current_layout()
        if not layout:
            return pane_photos
        
        print(f"  🔄 Trying alternative photo combinations to reduce crop values...")
        
        for attempt in range(max_attempts):
            # Try to find alternative photos for each pane
            new_pane_photos = {}
            used_photos = set()
            
            for pane in layout.panes:
                if pane.name not in self.pane_photos or not self.pane_photos[pane.name]:
                    continue
                
                photos = self.pane_photos[pane.name]
                current_index = self.pane_photo_indices.get(pane.name, 0)
                
                # Try a few different photos for this pane
                for offset in range(min(5, len(photos))):
                    try_index = (current_index + offset) % len(photos)
                    photo = photos[try_index]
                    
                    if photo.filepath not in used_photos:
                        new_pane_photos[pane.name] = photo
                        used_photos.add(photo.filepath)
                        break
                
                # If we couldn't find an alternative, use the original
                if pane.name not in new_pane_photos and pane.name in pane_photos:
                    new_pane_photos[pane.name] = pane_photos[pane.name]
                    used_photos.add(pane_photos[pane.name].filepath)
            
            # Check if the new combination has better crop values
            if new_pane_photos and self.validate_photo_layout(new_pane_photos):
                print(f"  ✅ Found better photo combination on attempt {attempt + 1}")
                return new_pane_photos
            
            # Update indices for next attempt
            for pane_name in new_pane_photos:
                if pane_name in self.pane_photo_indices:
                    self.pane_photo_indices[pane_name] = (self.pane_photo_indices[pane_name] + 1) % len(self.pane_photos[pane_name])
        
        print(f"  ⚠️  Could not find better photo combination after {max_attempts} attempts")
        return pane_photos
    
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
        """Special photo selection for dual pane: one square and one 4:3 vertical using new criteria"""
        layout = self.layout_manager.get_current_layout()
        pane_photos = {}
        
        print(f"🔍 Randomly selecting dual pane photos (one square + one 4:3 vertical) with new criteria...")
        
        # Get available photos for each required category with time weighting
        photos_by_category = getattr(self, 'all_photos_by_category', {})
        
        weighted_square_photos = self.get_available_photos_for_category("square", photos_by_category)
        weighted_43_vertical_photos = self.get_available_photos_for_category("4:3_vertical", photos_by_category)
        
        print(f"  📊 Available (weighted): {len(weighted_square_photos)} square choices, {len(weighted_43_vertical_photos)} 4:3 vertical choices")
        
        if not weighted_square_photos or not weighted_43_vertical_photos:
            print(f"  ⚠️  Cannot create dual pane layout: missing photo types")
            print(f"      Square photos available: {len(weighted_square_photos)}")
            print(f"      4:3 vertical photos available: {len(weighted_43_vertical_photos)}")
            return self._get_default_pane_photos()
        
        # Try different random combinations until we find one with acceptable crop values
        max_attempts = 20
        attempts = 0
        
        while attempts < max_attempts:
            # Randomly select photos with time weighting
            photo_square = random.choice(weighted_square_photos)
            photo_43_vertical = random.choice(weighted_43_vertical_photos)
            
            # Ensure no duplicates in the layout
            if photo_square.filepath == photo_43_vertical.filepath:
                attempts += 1
                continue
            
            # Randomly assign to left/right panes
            panes = list(layout.panes)
            random.shuffle(panes)
            
            pane_photos[panes[0].name] = photo_square
            pane_photos[panes[1].name] = photo_43_vertical
            
            # Validate the crop values
            if self.validate_photo_layout(pane_photos):
                # Mark photos as used in their categories
                self.mark_photo_as_used(photo_square)
                self.mark_photo_as_used(photo_43_vertical)
                
                square_indicator = "🌟" if photo_square.filepath in self.time_weighted_photos else "📷"
                vertical_indicator = "🌟" if photo_43_vertical.filepath in self.time_weighted_photos else "📷"
                
                print(f"  ✅ {square_indicator} Selected square photo: {os.path.basename(photo_square.filepath)} → {panes[0].name} pane")
                print(f"  ✅ {vertical_indicator} Selected 4:3 vertical photo: {os.path.basename(photo_43_vertical.filepath)} → {panes[1].name} pane")
                
                return pane_photos
            
            attempts += 1
        
        # If we couldn't find a good combination, use the last one but warn about crop
        print(f"  ⚠️  Could not find photo combination with crop < 0.2 after {attempts} attempts")
        print(f"  ⚠️  Using last combination (may have excessive cropping)")
        
        # Mark photos as used even if crop validation failed
        if pane_photos:
            for photo in pane_photos.values():
                self.mark_photo_as_used(photo)
        
        return pane_photos
    
    def _get_default_pane_photos(self) -> Dict[str, PhotoMetadata]:
        """Default photo selection using new random selection with repetition reduction and time weighting"""
        layout = self.layout_manager.get_current_layout()
        pane_photos = {}
        used_in_layout = set()  # Track photos used in current layout to prevent duplicates
        
        print(f"🔍 Randomly selecting unique photos for {len(layout.panes)} panes with new criteria...")
        
        # Get all photos by category for this layout
        photos_by_category = getattr(self, 'all_photos_by_category', {})
        
        for pane in layout.panes:
            print(f"  📱 {pane.name.capitalize()} pane: Selecting from categories {pane.photo_categories}")
            
            selected_photo = None
            attempts = 0
            max_attempts = 50  # Reasonable limit to prevent infinite loops
            
            while attempts < max_attempts and not selected_photo:
                # Get available photos for each category this pane accepts
                all_candidate_photos = []
                for category in pane.photo_categories:
                    weighted_photos = self.get_available_photos_for_category(category, photos_by_category)
                    all_candidate_photos.extend(weighted_photos)
                
                if not all_candidate_photos:
                    print(f"    ⚠️  No available photos for {pane.name} pane")
                    break
                
                # Randomly select from weighted candidates
                candidate_photo = random.choice(all_candidate_photos)
                
                # Check if this photo is already used in current layout
                if candidate_photo.filepath not in used_in_layout:
                    selected_photo = candidate_photo
                    used_in_layout.add(candidate_photo.filepath)
                    pane_photos[pane.name] = selected_photo
                    
                    # Mark photo as used in its category
                    self.mark_photo_as_used(selected_photo)
                    
                    time_indicator = "🌟" if selected_photo.filepath in self.time_weighted_photos else "📷"
                    print(f"    ✅ {time_indicator} Selected: {os.path.basename(selected_photo.filepath)} (category: {selected_photo.aspect_ratio_category})")
                    break
                
                attempts += 1
            
            if not selected_photo:
                print(f"    ⚠️  Could not find unique photo for {pane.name} pane after {attempts} attempts")
        
        print(f"🎯 Final random photo selection: {len(pane_photos)} panes filled")
        for pane_name, photo in pane_photos.items():
            time_indicator = "🌟" if photo.filepath in self.time_weighted_photos else "📷"
            print(f"  {pane_name}: {time_indicator} {photo.aspect_ratio_category} photo")
        
        # Validate the crop values for the selected photos
        if not self.validate_photo_layout(pane_photos):
            print(f"  ⚠️  Photo layout has excessive cropping (>0.2), trying alternatives...")
            # Try to find alternative photo combinations with better crop values
            alternative_photos = self.try_alternative_photo_combinations(pane_photos)
            if alternative_photos != pane_photos:
                print(f"  ✅ Found better photo combination with reduced cropping")
                return alternative_photos
            else:
                print(f"  ⚠️  Could not find better combination, continuing with current selection")
        
        return pane_photos
