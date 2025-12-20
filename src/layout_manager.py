"""
Layout management module for different screen layouts.
"""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class LayoutType(Enum):
    """Available layout types"""
    SINGLE_PANE = "single_pane"
    DUAL_PANE = "dual_pane"
    TRIPLE_PANE = "triple_pane"
    THREE_MIXED = "three_mixed"
    FOUR_PHOTOS = "four_photos"
    FIVE_PHOTOS = "five_photos"
    SIX_PHOTOS = "six_photos"
    
    # Future layouts can be added here


@dataclass
class Pane:
    """Represents a single pane in a layout"""
    x: int
    y: int
    width: int
    height: int
    photo_categories: List[str]
    name: str


@dataclass
class Layout:
    """Represents a complete screen layout"""
    name: str
    type: LayoutType
    panes: List[Pane]
    total_width: int
    total_height: int
    display_duration: int  # How long to show this layout (in milliseconds)


class LayoutManager:
    """Manages different screen layouts and pane configurations"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_layout = None
        self.current_layout_index = 0
        self.available_layouts = self._create_available_layouts()

    
    def _create_available_layouts(self) -> List[Layout]:
        """Create all available layouts based on screen dimensions"""
        layouts = []
        
        # Single pane layout (original behavior)
        layouts.append(Layout(
            name="Single Pane",
            type=LayoutType.SINGLE_PANE,
            panes=[
                Pane(
                    x=0, y=0,
                    width=self.screen_width,
                    height=self.screen_height,
                    photo_categories=["ultra_wide", "16:9_landscape", 
                                   "4:3_landscape"],
                    name="main"
                )
            ],
            total_width=self.screen_width,
            total_height=self.screen_height,
            display_duration=30000  # 30 seconds
        ))
        
        # Dual pane layout (as shown in the image)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Calculate proportional dimensions for the dual pane layout
            # Based on the image: left pane is ~60% width, right pane is ~40% width
            left_width = int(self.screen_width * 0.6)
            right_width = self.screen_width - left_width
            
            layouts.append(Layout(
                name="Dual Pane",
                type=LayoutType.DUAL_PANE,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=left_width,
                        height=self.screen_height,
                        photo_categories=["4:3_vertical", "square"],
                        name="left"
                    ),
                    Pane(
                        x=left_width, y=0,
                        width=right_width,
                        height=self.screen_height,
                        photo_categories=["4:3_vertical", "square"],
                        name="right"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        # Triple Vertical layout (left, center, right)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            pane_width = self.screen_width // 3
            
            layouts.append(Layout(
                name="Triple Vertical",
                type=LayoutType.TRIPLE_PANE,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=pane_width,
                        height=self.screen_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
                        name="left"
                    ),
                    Pane(
                        x=pane_width, y=0,
                        width=pane_width,
                        height=self.screen_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
                        name="center"
                    ),
                    Pane(
                        x=pane_width * 2, y=0,
                        width=pane_width,
                        height=self.screen_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
                        name="right"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        # Three mixed photos layout (left vertical, top-right square/landscape, bottom-right landscape)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Calculate dimensions based on the design from the screenshot
            # Left pane: ~56% width (1440px on 2560), full height
            left_width = int(self.screen_width * 0.56)
            right_width = self.screen_width - left_width
            
            # Right side split: top and bottom
            # Top-right pane: ~52% of height (750px on 1440)
            top_height = int(self.screen_height * 0.52)
            bottom_height = self.screen_height - top_height
            
            layouts.append(Layout(
                name="Three Mixed Photos",
                type=LayoutType.THREE_MIXED,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=left_width,
                        height=self.screen_height,
                        photo_categories=["4:3_vertical", "square", "16:9_vertical", "4:3_landscape", "16:9_landscape", "ultra_wide"],
                        name="left"
                    ),
                    Pane(
                        x=left_width, y=0,
                        width=right_width,
                        height=top_height,
                        photo_categories=["square", "4:3_landscape", "16:9_landscape", "4:3_vertical", "16:9_vertical", "ultra_wide"],
                        name="top_right"
                    ),
                    Pane(
                        x=left_width, y=top_height,
                        width=right_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="bottom_right"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        # Four photos layout (top-left, top-middle, right vertical, bottom landscape)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Calculate dimensions based on the design from the screenshot
            # Top-left width: ~30% (765px on 2560)
            top_left_width = int(self.screen_width * 0.30)
            # Top-middle width: ~21% (545px on 2560)
            top_middle_width = int(self.screen_width * 0.21)
            # Right pane width: remaining width
            right_width = self.screen_width - top_left_width - top_middle_width
            
            # Top height: ~38% (545px on 1440)
            top_height = int(self.screen_height * 0.38)
            # Bottom height: remaining height
            bottom_height = self.screen_height - top_height
            
            layouts.append(Layout(
                name="Four Photos",
                type=LayoutType.FOUR_PHOTOS,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=top_left_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="top_left"
                    ),
                    Pane(
                        x=top_left_width, y=0,
                        width=top_middle_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="top_middle"
                    ),
                    Pane(
                        x=top_left_width + top_middle_width, y=0,
                        width=right_width,
                        height=self.screen_height,
                        photo_categories=["16:9_vertical", "4:3_vertical", "square", "16:9_landscape", "4:3_landscape", "ultra_wide"],
                        name="right"
                    ),
                    Pane(
                        x=0, y=top_height,
                        width=top_left_width + top_middle_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="bottom"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        # Five photos layout (top-left, top-middle, top-right tall, bottom-left, bottom-right)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Calculate dimensions based on the design from the screenshot
            # Left section width: ~58% (1485px on 2560) - contains green + blue
            left_section_width = int(self.screen_width * 0.58)
            # Right section width: ~42% (1075px on 2560) - contains pink + yellow
            right_section_width = self.screen_width - left_section_width
            
            # Split left section vertically
            # Top-left width: ~29% of left (740px / 1485px ≈ 50% of left section)
            top_left_width = int(left_section_width * 0.50)
            top_middle_width = left_section_width - top_left_width
            
            # Top section height: ~41% (590px on 1440)
            top_height = int(self.screen_height * 0.41)
            # Bottom section height: ~59% (850px on 1440)
            bottom_height = self.screen_height - top_height
            
            # Bottom-right height: smaller portion of bottom
            bottom_right_height = int(bottom_height * 0.79)  # 675/850 ≈ 0.79
            bottom_right_top = top_height + (bottom_height - bottom_right_height)
            
            layouts.append(Layout(
                name="Five Photos",
                type=LayoutType.FIVE_PHOTOS,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=top_left_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="top_left"
                    ),
                    Pane(
                        x=top_left_width, y=0,
                        width=top_middle_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="top_middle"
                    ),
                    Pane(
                        x=left_section_width, y=0,
                        width=right_section_width,
                        height=self.screen_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="right"
                    ),
                    Pane(
                        x=0, y=top_height,
                        width=left_section_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="bottom_left"
                    ),
                    Pane(
                        x=left_section_width, y=bottom_right_top,
                        width=right_section_width,
                        height=bottom_right_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="bottom_right"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        # Six photos layout (2x3 grid with varying sizes)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Calculate dimensions based on the design from the screenshot
            # Top section: beige (19%), yellow (36%), magenta (45%)
            top_left_width = int(self.screen_width * 0.19)
            top_middle_width = int(self.screen_width * 0.36)
            top_right_width = self.screen_width - top_left_width - top_middle_width
            
            # Top height: ~44% (635px on 1440)
            top_height = int(self.screen_height * 0.44)
            # Bottom height: ~56% (805px on 1440)
            bottom_height = self.screen_height - top_height
            
            # Bottom section: green (55%), cyan (26%), purple (19%)
            bottom_left_width = int(self.screen_width * 0.55)
            bottom_middle_width = int(self.screen_width * 0.26)
            bottom_right_width = self.screen_width - bottom_left_width - bottom_middle_width
            
            layouts.append(Layout(
                name="Six Photos",
                type=LayoutType.SIX_PHOTOS,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=top_left_width,
                        height=top_height,
                        photo_categories=["4:3_vertical", "16:9_vertical", "square", "16:9_landscape", "4:3_landscape", "ultra_wide"],
                        name="top_left"
                    ),
                    Pane(
                        x=top_left_width, y=0,
                        width=top_middle_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="top_middle"
                    ),
                    Pane(
                        x=top_left_width + top_middle_width, y=0,
                        width=top_right_width,
                        height=self.screen_height,
                        photo_categories=["square", "4:3_landscape", "16:9_landscape", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="top_right"
                    ),
                    Pane(
                        x=0, y=top_height,
                        width=bottom_left_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="bottom_left"
                    ),
                    Pane(
                        x=bottom_left_width, y=top_height,
                        width=bottom_middle_width,
                        height=bottom_height,
                        photo_categories=["square", "16:9_landscape", "4:3_landscape", "16:9_vertical", "4:3_vertical", "ultra_wide"],
                        name="bottom_middle"
                    ),
                    Pane(
                        x=bottom_left_width + bottom_middle_width, y=top_height,
                        width=bottom_right_width,
                        height=bottom_height,
                        photo_categories=["4:3_vertical", "16:9_vertical", "square", "16:9_landscape", "4:3_landscape", "ultra_wide"],
                        name="bottom_right"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        return layouts
    
    def get_layout(self, layout_name: str) -> Optional[Layout]:
        """Get a specific layout by name"""
        # Normalize layout name for comparison
        normalized_name = layout_name.lower().replace("_", " ").replace("-", " ")
        
        for layout in self.available_layouts:
            # Normalize layout name for comparison
            layout_normalized = layout.name.lower()
            
            if layout_normalized == normalized_name:
                return layout
        
        # Try alternative matching if exact match fails
        for layout in self.available_layouts:
            if layout_name.lower() in layout.name.lower() or layout.name.lower() in layout_name.lower():
                return layout
        
        return None
    
    def get_available_layout_names(self) -> List[str]:
        """Get list of available layout names"""
        return [layout.name for layout in self.available_layouts]
    
    def get_available_layouts(self) -> List[Layout]:
        """Get list of all available layouts"""
        return self.available_layouts.copy()
    
    def set_current_layout(self, layout_name: str) -> bool:
        """Set the current active layout by name"""
        # Normalize layout name for comparison
        normalized_name = layout_name.lower().replace("_", " ").replace("-", " ")
        
        for i, layout in enumerate(self.available_layouts):
            # Normalize layout name for comparison
            layout_normalized = layout.name.lower()
            
            if layout_normalized == normalized_name:
                self.current_layout = layout
                self.current_layout_index = i
                return True
        
        # Try alternative matching if exact match fails
        for i, layout in enumerate(self.available_layouts):
            if layout_name.lower() in layout.name.lower() or layout.name.lower() in layout_name.lower():
                self.current_layout = layout
                self.current_layout_index = i
                return True
        
        return False
    
    def set_current_layout_by_index(self, index: int) -> bool:
        """Set the current active layout by index"""
        if 0 <= index < len(self.available_layouts):
            self.current_layout = self.available_layouts[index]
            self.current_layout_index = index
            return True
        return False
    
    def get_current_layout(self) -> Optional[Layout]:
        """Get the current active layout"""
        return self.current_layout
    
    def get_current_layout_index(self) -> int:
        """Get the index of the current layout"""
        return self.current_layout_index
    
    def get_default_layout(self) -> Layout:
        """Get the default layout (first available)"""
        return self.available_layouts[0] if self.available_layouts else None
    
    def can_use_layout(self, layout_name: str) -> bool:
        """Check if a layout can be used with current screen dimensions"""
        return self.get_layout(layout_name) is not None
    
    def get_next_layout(self) -> Optional[Layout]:
        """Get the next layout using weighted random selection"""
        if not self.available_layouts:
            return None
        
        # Use weighted random selection instead of sequential rotation
        return self._get_random_layout_by_weight()
    
    def rotate_to_next_layout(self) -> Optional[Layout]:
        """Rotate to a randomly selected layout based on weights and return it"""
        next_layout = self.get_next_layout()
        if next_layout:
            # Find the index of the selected layout
            for i, layout in enumerate(self.available_layouts):
                if layout.name == next_layout.name:
                    self.current_layout = next_layout
                    self.current_layout_index = i
                    break
        return next_layout
    
    def _get_random_layout_by_weight(self) -> Optional[Layout]:
        """Select a random layout based on weighted probabilities"""
        if not self.available_layouts:
            return None
        
        # Define layout weights based on user requirements
        # TEST MODE: Set Six Photos to 100% for testing
        layout_weights = {
            "Single Pane": 0,            # 0% probability (TEST)
            "Dual Pane": 0,              # 0% probability (TEST)
            "Triple Vertical": 0,        # 0% probability (TEST)
            "Three Mixed Photos": 0,     # 0% probability (TEST)
            "Four Photos": 0,            # 0% probability (TEST)
            "Five Photos": 0,            # 0% probability (TEST)
            "Six Photos": 100            # 100% probability (TEST)
        }
        
        # Create a list of layouts with their weights
        weighted_layouts = []
        for layout in self.available_layouts:
            weight = layout_weights.get(layout.name, 0)
            if weight > 0:
                weighted_layouts.extend([layout] * weight)
        
        if not weighted_layouts:
            # Fallback to uniform random selection if no weights match
            return random.choice(self.available_layouts)
        
        # Select a random layout based on weights
        selected_layout = random.choice(weighted_layouts)
        
        # Debug logging
        print(f"🎲 Weighted layout selection: {selected_layout.name} (weights: Single=78%, Dual=12%, Triple=10%)")
        
        return selected_layout
    
    def get_photo_categories_for_pane(self, pane_name: str) -> List[str]:
        """Get photo categories that can be displayed in a specific pane"""
        if not self.current_layout:
            return []
        
        for pane in self.current_layout.panes:
            if pane.name == pane_name:
                return pane.photo_categories
        return []
    
    def get_pane_dimensions(self, pane_name: str) -> Optional[Tuple[int, int, int, int]]:
        """Get dimensions (x, y, width, height) for a specific pane"""
        if not self.current_layout:
            return None
        
        for pane in self.current_layout.panes:
            if pane.name == pane_name:
                return (pane.x, pane.y, pane.width, pane.height)
        return None
    
    def get_current_layout_duration(self) -> int:
        """Get the display duration for the current layout"""
        if self.current_layout:
            return self.current_layout.display_duration
        return 30000  # Default 30 seconds
    

    
    def get_layout_count(self) -> int:
        """Get the total number of available layouts"""
        return len(self.available_layouts)
