import os
import random
import pygame
import glob
import math
from datetime import datetime, timedelta

# Configuration
SOURCE_FOLDER = "E:\Pictures To Check\Test"
SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1440
INACTIVITY_TIMEOUT = 60  # seconds
ZOOM_DURATION = 14  # seconds
TRANSITION_DURATION = 1.5  # seconds
PHOTO_DISPLAY_DURATION = 15  # seconds
TIME_WEIGHT_DAYS = 7
TIME_WEIGHT_MULTIPLIER = 3
FPS = 60

# Layout probabilities
LAYOUT_PROBABILITIES = {
    "one_photo": 0.70,
    "two_photos": 0.08,
    "three_vertical_photos": 0.05,
    "three_mixed_photos": 0.08,
    "four_photos": 0.04,
    "five_photos": 0.04,
    "six_photos": 0.01,
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


class NoPhotosError(Exception):
    pass

# Helper functions
def load_photos(folder):
    photos = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    file_path = os.path.join(root, file)
                    img = pygame.image.load(file_path)
                    width, height = img.get_size()
                    date_taken = datetime.fromtimestamp(os.path.getmtime(file_path))
                    photos.append({
                        "path": file_path,
                        "image": img,
                        "width": width,
                        "height": height,
                        "date_taken": date_taken
                    })
                except Exception as e:
                    print(f"Failed to load image {file_path}: {e}")
    
    if not photos:
        raise NoPhotosError(f"No valid photos found in the specified folder or its subfolders: {folder}")
    
    return photos

def select_photos(photos, num_needed, used_photos=None):
    if used_photos is None:
        used_photos = {aspect: set() for aspect in ["16:9", "4:3", "1:1"]}
    
    today = datetime.now()
    selected = []
    
    while len(selected) < num_needed:
        weighted_photos = []
        for photo in photos:
            aspect = classify_photo(photo)
            
            # Apply time weighting
            photo_date = photo["date_taken"].replace(year=today.year)
            days_diff = abs((today - photo_date).days)
            if days_diff <= TIME_WEIGHT_DAYS or (365 - days_diff) <= TIME_WEIGHT_DAYS:
                weighted_photos.extend([photo] * TIME_WEIGHT_MULTIPLIER)
            
            weighted_photos.append(photo)
        
        # Prioritize unused photos
        unused_photos = [p for p in weighted_photos if p["path"] not in used_photos[classify_photo(p)]]
        
        if unused_photos:
            photo = random.choice(unused_photos)
        else:
            # If all photos have been used, select from all photos
            photo = random.choice(weighted_photos)
        
        selected.append(photo)
        aspect = classify_photo(photo)
        used_photos[aspect].add(photo["path"])
        
        # If all photos of this aspect have been used, reset the used set for this aspect
        if len(used_photos[aspect]) == len([p for p in photos if classify_photo(p) == aspect]):
            used_photos[aspect].clear()
    
    return selected

def classify_photo(photo):
    width, height = photo["width"], photo["height"]
    aspect_ratio = width / height
    
    if 0.9 <= aspect_ratio <= 1.1:
        return "1:1"
    elif (1.7 <= aspect_ratio <= 1.8) or (1/1.8 <= aspect_ratio <= 1/1.7):
        return "16:9"
    else:
        return "4:3"  # This includes both landscape and portrait 4:3


def display_photo(photo):
    screen.fill((0, 0, 0))
    img = pygame.transform.scale(photo["image"], (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(img, (0, 0))
    pygame.display.flip()

def linear_wipe_transition(screen, old_surface, new_surface, direction='left', duration=1.5):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - start_time) / 1000  # Convert to seconds
        
        if elapsed > duration:
            screen.blit(new_surface, (0, 0))
            pygame.display.flip()
            return
        
        progress = elapsed / duration
        eased_progress = 1 - math.pow(1 - progress, 4)  # Ease out quart
        
        offset = int(SCREEN_WIDTH * eased_progress)
        
        if direction == 'left':
            screen.blit(old_surface, (-offset, 0))
            screen.blit(new_surface, (SCREEN_WIDTH - offset, 0))
        else:
            screen.blit(old_surface, (offset, 0))
            screen.blit(new_surface, (-SCREEN_WIDTH + offset, 0))
        
        pygame.display.flip()
        clock.tick(FPS)

def dissolve_transition(screen, old_surfaces, new_surfaces, duration=1.5):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - start_time) / 1000  # Convert to seconds
        
        if elapsed > duration:
            for surface, pos in new_surfaces:
                screen.blit(surface, pos)
            pygame.display.flip()
            return
        
        screen.fill((0, 0, 0))
        
        for i, (new_surface, pos) in enumerate(new_surfaces):
            delay = i * 0.1  # 0.1 second delay between each frame
            frame_elapsed = max(0, elapsed - delay)
            if frame_elapsed > 0:
                alpha = min(255, int(frame_elapsed / 0.2 * 255))  # 0.2 seconds to reach full opacity
                new_surface.set_alpha(alpha)
                screen.blit(new_surface, pos)
        
        pygame.display.flip()
        clock.tick(FPS)

def zoom_effect(screen, surface, duration=14, zoom_factor=0.94):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    original_size = surface.get_size()
    
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - start_time) / 1000  # Convert to seconds
        
        if elapsed > duration:
            return
        
        progress = elapsed / duration
        current_zoom = 1 - (1 - zoom_factor) * progress
        
        zoomed_width = int(original_size[0] * current_zoom)
        zoomed_height = int(original_size[1] * current_zoom)
        zoomed_surface = pygame.transform.smoothscale(surface, (zoomed_width, zoomed_height))
        
        x_offset = (SCREEN_WIDTH - zoomed_width) // 2
        y_offset = (SCREEN_HEIGHT - zoomed_height) // 2
        
        screen.fill((0, 0, 0))
        screen.blit(zoomed_surface, (x_offset, y_offset))
        pygame.display.flip()
        
        clock.tick(FPS)

def display_layout(screen, layout, photos):
    surfaces = []
    for photo, (x, y, w, h) in zip(photos, layout):
        img = pygame.transform.scale(photo["image"], (w, h))
        surfaces.append((img, (x, y)))
    return surfaces

def generate_layouts():
    layouts = [
        # One photo layout
        [
            (0, 0, 2560, 1440)  # (x, y, width, height)
        ],
        
        # Two photos layout
        [
            (0, 0, 1280, 1440),
            (1280, 0, 1280, 1440)
        ],
        
        # Three vertical photos layout
        [
            (0, 0, 853, 1440),
            (853, 0, 854, 1440),
            (1707, 0, 853, 1440)
        ],
        
        # Three mixed photos layout
        [
            (0, 0, 1280, 1440),
            (1280, 0, 1280, 720),
            (1280, 720, 1280, 720)
        ],
        
        # Four photos layout
        [
            (0, 0, 1280, 720),
            (1280, 0, 1280, 720),
            (0, 720, 1280, 720),
            (1280, 720, 1280, 720)
        ],
        
        # Five photos layout
        [
            (0, 0, 1280, 720),
            (1280, 0, 1280, 720),
            (0, 720, 853, 720),
            (853, 720, 854, 720),
            (1707, 720, 853, 720)
        ],
        
        # Six photos layout
        [
            (0, 0, 853, 720),
            (853, 0, 854, 720),
            (1707, 0, 853, 720),
            (0, 720, 853, 720),
            (853, 720, 854, 720),
            (1707, 720, 853, 720)
        ]
    ]
    
    return layouts

# Layout probabilities
LAYOUT_PROBABILITIES = {
    0: 0.70,  # One photo
    1: 0.08,  # Two photos
    2: 0.05,  # Three vertical photos
    3: 0.08,  # Three mixed photos
    4: 0.04,  # Four photos
    5: 0.04,  # Five photos
    6: 0.01   # Six photos
}

# Pink layouts (example, adjust as needed)
PINK_LAYOUTS = [1, 3, 5]  # Two photos, Three mixed photos, Five photos

def select_layout(previous_layouts):
    while True:
        layout_index = random.choices(list(LAYOUT_PROBABILITIES.keys()), 
                                      weights=list(LAYOUT_PROBABILITIES.values()))[0]
        
        # Check pink layout rule
        if layout_index in PINK_LAYOUTS:
            if len(previous_layouts) < 5 or any(l in PINK_LAYOUTS for l in previous_layouts[-5:]):
                continue
        
        return layout_index

def run_screensaver(screen, photos, layouts):
    clock = pygame.time.Clock()
    current_layout = None
    current_photos = None
    
    while True:
        for event in pygame.event.get():
            if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                return

        new_layout = random.choice(layouts)
        new_photos = select_photos(photos, len(new_layout))
        new_surfaces = display_layout(screen, new_layout, new_photos)

        if current_layout is None:
            # First activation
            screen.fill((0, 0, 0))
            pygame.display.flip()
            pygame.time.wait(250)  # 0.25 seconds black screen
            dissolve_transition(screen, [], new_surfaces, duration=0.25)
        elif len(new_layout) == 1:
            # Transition to one photo layout
            direction = random.choice(['left', 'right'])
            linear_wipe_transition(screen, screen.copy(), new_surfaces[0][0], direction)
        else:
            # Transition to multi-photo layout
            dissolve_transition(screen, current_surfaces, new_surfaces)

        # Zoom effect
        for surface, pos in new_surfaces:
            zoom_effect(screen, surface)

        current_layout = new_layout
        current_photos = new_photos
        current_surfaces = new_surfaces

        clock.tick(FPS)

# Main execution
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    try:
        photos = load_photos(SOURCE_FOLDER)
        layouts = generate_layouts()  # You need to implement this function
        run_screensaver(screen, photos, layouts)        
    except NoPhotosError as e:
        print(e)

    pygame.quit()