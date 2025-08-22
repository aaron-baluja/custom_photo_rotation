# Custom Photo Rotation Screen Saver

A Python-based screen saver that displays images from a configured folder with automatic layout rotation. The program runs in fullscreen mode and recursively searches for images in subdirectories, classifies them by aspect ratio, and presents them in different layout modes that automatically rotate every 15 seconds.

## Supported Features

### Layout Modes
- **Single Pane**: Full-screen layout displaying one photo at a time
- **Dual Pane**: Two side-by-side panes for portrait photos (requires ≥1920x1080)
- **Triple Pane**: Three vertical panes for portrait photos (requires ≥1920x1080)

### Photo Classification
Automatically categorizes photos into 6 aspect ratio categories:
- **Ultra-Wide (21:9)**: Panoramic photos with letterboxing
- **16:9 Landscape**: Wide landscape photos
- **16:9 Vertical**: Tall portrait photos  
- **4:3 Landscape**: Standard landscape photos
- **4:3 Vertical**: Standard portrait photos
- **Square (1:1)**: Square photos

### Smart Features
- **Fullscreen Mode**: Runs in true fullscreen for authentic screen saver experience
- **Automatic Layout Rotation**: Cycles through available layouts every 15 seconds
- **Intelligent Photo Placement**: Photos automatically assigned to appropriate panes
- **Aspect Ratio Preservation**: Photos maintain their natural proportions
- **Recursive Search**: Finds images in all subdirectories
- **Comprehensive Logging**: Automatic log file creation with timestamps

## Configuration Options

### Basic Settings
Create a `config.txt` file in the same directory as `main.py`:

```
# Image folder path
IMAGE_FOLDER=C:\Users\YourName\Pictures\Screensaver

# Display settings
CHANGE_INTERVAL=15000

# Layout settings
LAYOUT_TYPE=auto
```

### Configuration Parameters
- **`IMAGE_FOLDER`**: Path to folder containing your images

- **`CHANGE_INTERVAL`**: How often layouts and photos change (milliseconds, default: 15000)
- **`LAYOUT_TYPE`**: `auto` for rotation, or specific layout name (`single_pane`, `dual_pane`, `triple_pane`)


### Supported Image Formats
- JPG/JPEG
- PNG

## Debug Controls and Usage

### Keyboard Controls
- **`v`**: Toggle debug overlay visibility (shows photo metadata)
- **`Enter`**: Manually advance to next layout/photo combination
- **`Left Control`**: Start issue reporting mode (timer pauses, photos stop changing)
- **`Left Control` (again): Finish issue reporting and resume normal operation
- **`Escape`**: Cancel issue reporting or exit screen saver
- **Any other key**: Exit screen saver

### Debug Overlay Information
When enabled, each photo displays:
- Pane name and photo filename
- Aspect ratio classification
- Original and display dimensions
- Category error (difference from target ratio)
- Display crop/letterbox information
- Date taken

### Issue Reporting System
1. Press **Left Control** when you notice an issue
2. Type your description (supports multi-line with Enter key)
3. Press **Left Control** again to finish and resume
4. All reports are logged with timestamps and context

### Logging System
- Automatically creates `logs/` folder
- Generates timestamped log files for each session
- Captures all console output, debug information, and issue reports
- Useful for troubleshooting and monitoring

## Implementation Details

### Architecture
- **Modular Design**: Separate modules for photo classification, layout management, and photo selection
- **Tkinter GUI**: Python's standard GUI toolkit for cross-platform compatibility
- **PIL/Pillow**: Image processing and metadata extraction
- **Configurable Tolerance**: Adjustable aspect ratio classification thresholds

### Photo Display Strategy
- **Ultra-Wide Photos**: Letterboxed to maintain aspect ratio
- **Standard Photos**: Cropped to fill panes while preserving aspect ratio
- **Orientation-Aware Cropping**: Landscape photos cropped from top/bottom, vertical from left/right

### Photo Selection Logic
- **Repetition Reduction**: Photos don't repeat within a category until all others are shown
- **Time Weighting**: Photos taken around current date appear 3x more often
- **Layout Uniqueness**: No photo appears twice in the same layout
- **Crop Validation**: Rejects layouts with excessive cropping (>0.2 threshold)

### Layout Rotation System
- **Weighted Random Selection**: Single Pane (78%), Dual Pane (12%), Triple Pane (10%)
- **Screen Resolution Detection**: Automatically determines available layouts
- **Fallback Handling**: Gracefully handles unsupported layouts

### Performance Considerations
- **Efficient Image Loading**: Images loaded on-demand for each pane
- **Memory Management**: Proper cleanup of image resources
- **Timer Management**: Robust cancellation to prevent overlapping rotations

### Requirements
- **Python**: 3.7 or higher
- **Dependencies**: Install via `pip install -r requirements.txt`
- **Screen Resolution**: ≥1920x1080 for multi-pane layouts
- **Operating System**: Windows, macOS, or Linux

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the screen saver
python main.py

# Test layout system
python demo_layouts.py
```
