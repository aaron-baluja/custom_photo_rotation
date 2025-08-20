"""
Photo classification module for aspect ratio categorization.
"""

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
    
    def get_all_categories(self):
        """Get list of all available categories"""
        return list(self.aspect_ratios.keys())
    
    def get_category_tolerance(self, category):
        """Get tolerance for a specific category"""
        return self.aspect_ratios.get(category, {}).get('tolerance', 0.0)
