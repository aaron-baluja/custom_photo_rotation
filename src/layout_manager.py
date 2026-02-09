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
    
    def __init__(self, screen_width: int, screen_height: int, layout_weights: Optional[Dict[str, int]] = None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_layout = None
        self.current_layout_index = 0
        self.available_layouts = self._create_available_layouts()
        
        # Set layout weights (use provided weights or defaults)
        if layout_weights:
            self.layout_weights = layout_weights
        else:
            # Default layout weights
            self.layout_weights = {
                "Single Pane": 70,
                "Dual Pane": 8,
                "Triple Vertical": 5,
                "Three Mixed Photos": 8,
                "Four Photos": 4,
                "Five Photos": 4,
                "Six Photos": 1
            }
        
        # Pink layout exclusion rule tracking
        # Pink layouts: Four Photos, Five Photos, Six Photos
        self.pink_layouts = {"Four Photos", "Five Photos", "Six Photos"}
        self.non_pink_layouts = {"Single Pane", "Dual Pane", "Triple Vertical", "Three Mixed Photos"}
        self.last_pink_layout_shown = False
        self.non_pink_count_since_pink = 0

    
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
        
        # Three mixed photos layout (diagram-aligned)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Target sizes at 2560x1440 (from diagram)
            # Left pane: 1510x1440
            # Top-right: 1050x750
            # Bottom-right: 1050x690
            left_width = round(self.screen_width * (1510 / 2560))
            right_width = self.screen_width - left_width
            top_height = round(self.screen_height * (750 / 1440))
            bottom_height = self.screen_height - top_height
            
            layouts.append(Layout(
                name="Three Mixed Photos",
                type=LayoutType.THREE_MIXED,
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
                        height=top_height,
                        photo_categories=["square", "4:3_landscape"],
                        name="top_right"
                    ),
                    Pane(
                        x=left_width, y=top_height,
                        width=right_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape"],
                        name="bottom_right"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        # Four photos layout (diagram-aligned)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Target sizes at 2560x1440 (from diagram)
            # Top-left: 765x545
            # Top-middle: 770x545
            # Right: 1025x1440
            # Bottom: 1535x895
            top_left_width = round(self.screen_width * (765 / 2560))
            top_middle_width = round(self.screen_width * (770 / 2560))
            left_section_width = top_left_width + top_middle_width
            right_width = self.screen_width - left_section_width
            
            top_height = round(self.screen_height * (545 / 1440))
            bottom_height = self.screen_height - top_height
            
            layouts.append(Layout(
                name="Four Photos",
                type=LayoutType.FOUR_PHOTOS,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=top_left_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square"],
                        name="top_left"
                    ),
                    Pane(
                        x=top_left_width, y=0,
                        width=top_middle_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square"],
                        name="top_middle"
                    ),
                    Pane(
                        x=top_left_width + top_middle_width, y=0,
                        width=right_width,
                        height=self.screen_height,
                        photo_categories=["16:9_vertical", "4:3_vertical"],
                        name="right"
                    ),
                    Pane(
                        x=0, y=top_height,
                        width=left_section_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape"],
                        name="bottom"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))
        
        # Five photos layout (diagram-aligned)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Target sizes at 2560x1440 (from diagram)
            # Left section: 1485x1440, right section: 1075x1440
            # Top-left: 740x590, Top-middle: 745x590
            # Top-right: 1075x765, Bottom-left: 1485x850, Bottom-right: 1075x675
            left_section_width = round(self.screen_width * (1485 / 2560))
            right_section_width = self.screen_width - left_section_width

            top_height = round(self.screen_height * (590 / 1440))
            bottom_height = self.screen_height - top_height

            top_left_width = round(left_section_width * (740 / 1485))
            top_middle_width = left_section_width - top_left_width

            top_right_height = round(self.screen_height * (765 / 1440))
            bottom_right_height = self.screen_height - top_right_height

            layouts.append(Layout(
                name="Five Photos",
                type=LayoutType.FIVE_PHOTOS,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=top_left_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square"],
                        name="top_left"
                    ),
                    Pane(
                        x=top_left_width, y=0,
                        width=top_middle_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square"],
                        name="top_middle"
                    ),
                    Pane(
                        x=left_section_width, y=0,
                        width=right_section_width,
                        height=top_right_height,
                        photo_categories=["16:9_landscape", "4:3_landscape", "square"],
                        name="top_right"
                    ),
                    Pane(
                        x=0, y=top_height,
                        width=left_section_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape"],
                        name="bottom_left"
                    ),
                    Pane(
                        x=left_section_width, y=top_right_height,
                        width=right_section_width,
                        height=bottom_right_height,
                        photo_categories=["16:9_landscape", "4:3_landscape"],
                        name="bottom_right"
                    )
                ],
                total_width=self.screen_width,
                total_height=self.screen_height,
                display_duration=30000  # 30 seconds
            ))

        # Six photos layout (diagram-aligned)
        if self.screen_width >= 1920 and self.screen_height >= 1080:
            # Target sizes at 2560x1440 (from diagram)
            # Top widths: 485, 920, 1155
            # Bottom widths: 1405, 670, 485
            # Heights: left/middle 635/805, right 820/620
            left_width = round(self.screen_width * (485 / 2560))
            middle_width = round(self.screen_width * (920 / 2560))
            right_width = self.screen_width - left_width - middle_width

            top_height = round(self.screen_height * (635 / 1440))
            bottom_height = self.screen_height - top_height

            right_top_height = round(self.screen_height * (820 / 1440))
            right_bottom_height = self.screen_height - right_top_height

            bottom_left_width = left_width + middle_width
            bottom_middle_width = round(self.screen_width * (670 / 2560))
            bottom_right_width = self.screen_width - bottom_left_width - bottom_middle_width

            layouts.append(Layout(
                name="Six Photos",
                type=LayoutType.SIX_PHOTOS,
                panes=[
                    Pane(
                        x=0, y=0,
                        width=left_width,
                        height=top_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
                        name="top_left"
                    ),
                    Pane(
                        x=left_width, y=0,
                        width=middle_width,
                        height=top_height,
                        photo_categories=["16:9_landscape", "4:3_landscape"],
                        name="top_middle"
                    ),
                    Pane(
                        x=bottom_left_width, y=0,
                        width=right_width,
                        height=right_top_height,
                        photo_categories=["square", "4:3_landscape"],
                        name="top_right"
                    ),
                    Pane(
                        x=0, y=top_height,
                        width=bottom_left_width,
                        height=bottom_height,
                        photo_categories=["16:9_landscape", "4:3_landscape"],
                        name="bottom_left"
                    ),
                    Pane(
                        x=bottom_left_width, y=right_top_height,
                        width=bottom_middle_width,
                        height=right_bottom_height,
                        photo_categories=["square"],
                        name="bottom_middle"
                    ),
                    Pane(
                        x=bottom_left_width + bottom_middle_width, y=right_top_height,
                        width=bottom_right_width,
                        height=right_bottom_height,
                        photo_categories=["4:3_vertical", "16:9_vertical"],
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
        """Rotate to a randomly selected layout based on weights and apply pink layout tracking"""
        next_layout = self.get_next_layout()
        if next_layout:
            # Find the index of the selected layout
            for i, layout in enumerate(self.available_layouts):
                if layout.name == next_layout.name:
                    self.current_layout = next_layout
                    self.current_layout_index = i
                    
                    # Update pink layout tracking
                    if next_layout.name in self.pink_layouts:
                        # Pink layout selected - reset counter
                        self.last_pink_layout_shown = True
                        self.non_pink_count_since_pink = 0
                        print(f"🎨 Pink layout selected: {next_layout.name}. Must show 5 non-pink layouts before another pink layout.")
                    else:
                        # Non-pink layout selected - increment counter if tracking
                        if self.last_pink_layout_shown:
                            self.non_pink_count_since_pink += 1
                            if self.non_pink_count_since_pink >= 5:
                                self.last_pink_layout_shown = False
                                print(f"✅ 5 non-pink layouts shown. Pink layouts are now available again.")
                    break
        return next_layout
    
    def _get_random_layout_by_weight(self) -> Optional[Layout]:
        """Select a random layout based on weighted probabilities with pink layout restrictions"""
        if not self.available_layouts:
            return None
        
        # Use instance weights (can be customized from config file)
        # Create a list of layouts with their weights
        weighted_layouts = []
        
        # If last layout was pink and we haven't shown 5+ non-pink layouts, exclude pink layouts
        if self.last_pink_layout_shown and self.non_pink_count_since_pink < 5:
            # Exclude pink layouts from selection
            for layout in self.available_layouts:
                weight = self.layout_weights.get(layout.name, 0)
                if weight > 0 and layout.name in self.non_pink_layouts:
                    weighted_layouts.extend([layout] * weight)
            
            if not weighted_layouts:
                # Fallback: if no non-pink layouts available, allow pink layouts
                for layout in self.available_layouts:
                    weight = self.layout_weights.get(layout.name, 0)
                    if weight > 0:
                        weighted_layouts.extend([layout] * weight)
        else:
            # Normal selection - include all layouts
            for layout in self.available_layouts:
                weight = self.layout_weights.get(layout.name, 0)
                if weight > 0:
                    weighted_layouts.extend([layout] * weight)
        
        if not weighted_layouts:
            # Fallback to uniform random selection if no layouts available
            return random.choice(self.available_layouts)
        
        # Select a random layout based on weights
        selected_layout = random.choice(weighted_layouts)
        
        # Debug logging
        debug_info = f"🎲 Weighted layout selection: {selected_layout.name}"
        if self.last_pink_layout_shown and self.non_pink_count_since_pink < 5:
            debug_info += f" (pink restricted: {self.non_pink_count_since_pink}/5 non-pink shown)"
        print(debug_info)
        
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
