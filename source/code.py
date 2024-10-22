import os
import random
import pygame
import glob
import math
import time
import sys
from datetime import datetime, timedelta

# Configuration
SOURCE_FOLDER_DEFAULT = "."
SCREEN_WIDTH = 2560
SCREEN_HEIGHT = 1440
INACTIVITY_TIMEOUT = 60  # seconds
ZOOM_DURATION = 14  # seconds
TRANSITION_DURATION = 1.5  # seconds
PHOTO_DISPLAY_DURATION = 15  # seconds
TIME_WEIGHT_DAYS = 7
TIME_WEIGHT_MULTIPLIER = 3
FPS = 60

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

def classify_photo(photo):
    aspect_ratio = photo["width"] / photo["height"]
    if 0.9 <= aspect_ratio <= 1.1:
        return "1:1"
    elif 1.7 <= aspect_ratio <= 1.8:
        return "16:9 landscape"
    elif 1/1.8 <= aspect_ratio <= 1/1.7:
        return "16:9 vertical"
    elif 1.3 <= aspect_ratio <= 1.4:
        return "4:3 landscape"
    elif 1/1.4 <= aspect_ratio <= 1/1.3:
        return "4:3 vertical"
    else:
        return "other"

def get_required_aspect(width, height):
    aspect_ratio = width / height
    if aspect_ratio == 16/9:
        return "16:9 landscape"
    elif aspect_ratio == 9/16:
        return "16:9 vertical"
    elif aspect_ratio == 4/3:
        return "4:3 landscape"
    elif aspect_ratio == 3/4:
        return "4:3 vertical"
    elif aspect_ratio == 1:
        return "1:1"
    else:
        return "other"

def select_photos(photos, layout, used_photos=None):
    if used_photos is None:
        used_photos = {aspect: set() for aspect in ["16:9 landscape", "16:9 vertical", "4:3 landscape", "4:3 vertical", "1:1", "other"]}
    
    today = datetime.now()
    selected = []
    
    for x, y, width, height in layout:
        required_aspect = get_required_aspect(width, height)
        weighted_photos = []
        
        for photo in photos:
            photo_aspect = classify_photo(photo)
            
            # Skip if the photo has been used and there are other unused photos of the same aspect ratio
            if photo["path"] in used_photos[photo_aspect] and len(used_photos[photo_aspect]) < len([p for p in photos if classify_photo(p) == photo_aspect]):
                continue
            if photo_aspect == required_aspect:            
                # Apply time weighting
                photo_date = photo["date_taken"].replace(year=today.year)
                days_diff = min(abs((today - photo_date).days), 365 - abs((today - photo_date).days))
                if days_diff <= 7:
                    weighted_photos.extend([photo] * 3)
                else:
                    weighted_photos.extend([photo] * 1)                    
            
            # # Add weight based on aspect ratio match

            #     weighted_photos.extend([photo] * 2)
            # elif photo_aspect.split()[0] == required_aspect.split()[0]:
            #     # Allow landscape to fit vertical and vice versa, but with lower weight
            #     weighted_photos.append(photo)
        
        if weighted_photos:
            chosen_photo = random.choice(weighted_photos)
            selected.append((chosen_photo, (x, y, width, height)))
            used_photos[classify_photo(chosen_photo)].add(chosen_photo["path"])
        # else:
            # If no suitable photo found, choose any unused photo
            
            # unused_photos = [p for p in photos if p["path"] not in used_photos[classify_photo(p)]]
            # if unused_photos:
            #     chosen_photo = random.choice(unused_photos)
            #     selected.append((chosen_photo, (x, y, width, height)))
            #     used_photos[classify_photo(chosen_photo)].add(chosen_photo["path"])
            # else:
            #     # If all photos have been used, reset used_photos and try again
            #     used_photos = {aspect: set() for aspect in ["16:9 landscape", "16:9 vertical", "4:3 landscape", "4:3 vertical", "1:1", "other"]}
            #     return select_photos(photos, layout, used_photos)
    
    return selected


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
            return True
        
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
        

def dissolve_transition(screen, old_surfaces, new_surfaces, duration=1.5):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    while True:
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - start_time) / 1000  # Convert to seconds
        
        if elapsed > duration:
            for surface, pos in new_surfaces:
                screen.blit(surface, pos)
            return True
        
        screen.fill((0, 0, 0))
        
        for i, (new_surface, pos) in enumerate(new_surfaces):
            delay = i * 0.1  # 0.1 second delay between each frame
            frame_elapsed = max(0, elapsed - delay)
            if frame_elapsed > 0:
                alpha = min(255, int(frame_elapsed / 0.2 * 255))  # 0.2 seconds to reach full opacity
                new_surface.set_alpha(alpha)
                screen.blit(new_surface, pos)
        pygame.display.flip()
    

def display_layout(screen, selected_photos):
    surfaces = []
    # print ("New layout")
    for photo, (x, y, w, h) in selected_photos:
        # Load the image if it hasn't been loaded yet
        if isinstance(photo["image"], str):
            try:
                photo["image"] = pygame.image.load(photo["image"]).convert()
            except pygame.error as e:
                print(f"Error loading image {photo['path']}: {e}")
                continue

        # Calculate the scaling factor to fit the photo into the layout slot
        photo_aspect = photo["width"] / photo["height"]
        slot_aspect = w / h
        
        if photo_aspect > slot_aspect:
            # Photo is wider than the slot, scale based on height
            scale_factor = h / photo["height"]
        else:
            # Photo is taller than the slot, scale based on width
            scale_factor = w / photo["width"]
        
        # Calculate new dimensions
        new_width = int(photo["width"] * scale_factor)
        new_height = int(photo["height"] * scale_factor)
        
        # print (photo["width"], photo["height"], (x, y, w, h) , photo_aspect, slot_aspect)

        # Scale the image
        scaled_img = pygame.transform.smoothscale(photo["image"], (new_width, new_height))
        
        # Calculate position to center the image in the slot
        pos_x = x + (w - new_width) // 2
        pos_y = y + (h - new_height) // 2
        
        surfaces.append((scaled_img, (pos_x, pos_y)))
    
    return surfaces

def generate_layouts():
    layouts = [
        # One photo layout
        [
            (0, 0, 2560, 1440)  # (x, y, width, height)
        ],
        
        # # Two photos layout
        # [
        #     (0, 0, 1535, 1440),
        #     (1535, 0, 2560, 1440)
        # ],
        
        # Three vertical photos layout
        # [
        #     (0, 0, 853, 1440),
        #     (853, 0, 854, 1440),
        #     (1707, 0, 853, 1440)
        # ],
        
        # # Three mixed photos layout
        # [
        #     (0, 0, 1280, 1440),
        #     (1280, 0, 1280, 720),
        #     (1280, 720, 1280, 720)
        # ],
        
        # Four photos layout
        [
            (0, 0, 1280, 720),
            (1280, 0, 1280, 720),
            (0, 720, 1280, 720),
            (1280, 720, 1280, 720)
        ],
        
        # # Five photos layout
        # [
        #     (0, 0, 1280, 720),
        #     (1280, 0, 1280, 720),
        #     (0, 720, 853, 720),
        #     (853, 720, 854, 720),
        #     (1707, 720, 853, 720)
        # ],
        
        # # Six photos layout
        # [
        #     (0, 0, 853, 720),
        #     (853, 0, 854, 720),
        #     (1707, 0, 853, 720),
        #     (0, 720, 853, 720),
        #     (853, 720, 854, 720),
        #     (1707, 720, 853, 720)
        # ]
    ]
    
    return layouts

# Layout probabilities
LAYOUT_PROBABILITIES = {
    0: 0.70,  # One photo
    # 1: 0.08,  # Two photos
    # 2: 0.05,  # Three vertical photos
    # 3: 0.08,  # Three mixed photos
    4: 0.04,  # Four photos
    # 5: 0.04,  # Five photos
    # 6: 0.01   # Six photos
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
    current_surfaces = None
    last_update_time = 0
    update_interval = 10  # seconds
    transition_done = False
    
    while True:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type in [pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                return

        # if more than interval has passed, start update logic
        if current_time - last_update_time >= update_interval:
            while True: # try layouts until one that works
                new_layout = random.choice(layouts)
                new_photos = select_photos(photos, new_layout)
                if new_photos is not []:
                    new_surfaces = display_layout(screen, new_photos)            
                    break
            last_update_time = current_time
            transition_done = False
        elif transition_done is False:

            if current_layout is None:
                # First activation
                screen.fill((0, 0, 0))
                pygame.display.flip()
                pygame.time.wait(250)  # 0.25 seconds black screen
                transition_done = dissolve_transition(screen, [], new_surfaces, duration=0.25)
            elif len(new_layout) == 1:
                # Transition to one photo layout
                direction = random.choice(['left', 'right'])
                transition_done = linear_wipe_transition(screen, screen.copy(), new_surfaces[0][0], direction)
            else:
                # Transition to multi-photo layout
                transition_done = dissolve_transition(screen, current_surfaces, new_surfaces)

            current_layout = new_layout
            current_photos = new_photos
            current_surfaces = new_surfaces

            # # Apply zoom effect
            # zoomed_surfaces = []
            # zoom_progress = (current_time - last_update_time) / update_interval
            # zoom_factor = 1 - (1 - 0.94) * zoom_progress  # Zoom from 100% to 94%
            
            # for surface, (x, y) in current_surfaces:
            #     original_size = surface.get_size()
            #     zoomed_size = (int(original_size[0] * zoom_factor), int(original_size[1] * zoom_factor))
            #     zoomed_surface = pygame.transform.smoothscale(surface, zoomed_size)
                
            #     new_x = x + (original_size[0] - zoomed_size[0]) // 2
            #     new_y = y + (original_size[1] - zoomed_size[1]) // 2
                
            #     zoomed_surfaces.append((zoomed_surface, (new_x, new_y)))
            
            # screen.fill((0, 0, 0))
            # for surface, pos in zoomed_surfaces:
            #     screen.blit(surface, pos)

        clock.tick(FPS)
        pygame.display.flip()

# Main execution
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    if len(sys.argv) > 1:
        # Remove escape characters and normalize the path
        source_folder = (sys.argv[1])
    else:
        source_folder = SOURCE_FOLDER_DEFAULT

    try:
        photos = load_photos(source_folder)
        layouts = generate_layouts()
        run_screensaver(screen, photos, layouts)        
    except NoPhotosError as e:
        print(e)

    pygame.quit()