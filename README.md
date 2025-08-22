# Custom Photo Rotation Screen Saver

A Python-based screen saver application that displays images from a configured folder with automatic rotation every 15 seconds. The program recursively searches for images in all subdirectories and classifies them by aspect ratio for organized slideshow presentation. Now supports **multiple layout modes with automatic rotation** for a dynamic and engaging screen saver experience!

## Features

- **🎯 Multiple Layout Modes**: Single pane, dual-pane, triple-pane, and quad-pane layouts
- **🔄 Automatic Layout Rotation**: Seamlessly rotates through different layouts every 15 seconds
- **🧠 Smart Layout Selection**: Automatically chooses appropriate layouts based on screen resolution
- **📱 Intelligent Photo Placement**: Photos are automatically placed in appropriate panes based on their aspect ratio classification
- **⚙️ Flexible Configuration**: Easy switching between auto-rotation and specific layout modes
- **🔍 Debug Overlay System**: Toggle-able metadata overlays and manual layout advancement for testing and troubleshooting
- **📝 Comprehensive Logging**: Automatic log file creation with timestamped filenames
- **Fullscreen Display**: Runs in fullscreen mode for true screen saver experience
- **Smart Aspect Ratio Handling**: Automatically resizes images to fit screen while maintaining their original aspect ratio
- **15-Second Photo Intervals**: Each photo is displayed for exactly 15 seconds within each layout
- **Photo Classification**: Automatically categorizes photos into 6 aspect ratio categories
- **Metadata Extraction**: Extracts width, height, and date taken from photos
- **Multiple Formats**: Supports JPG, JPEG, and PNG formats
- **Easy Exit**: Press any key, click, or press Escape to exit
- **Config File**: Simple text file configuration for image folder path and layout preferences
- **Recursive Search**: Automatically finds images in all subdirectories
- **Organized Slideshow**: Photos are grouped by category and displayed in appropriate panes

## Layout Modes

### 🖼️ Single Pane Layout (Classic)
- **Description**: Traditional full-screen layout that displays one photo at a time
- **Photo Types**: All photo categories (ultra-wide, 16:9 landscape/vertical, 4:3 landscape/vertical, square)
- **Best For**: Standard displays and traditional screen saver experience
- **Display Duration**: 15 seconds before rotating to next layout

### 📱 Dual Pane Layout
- **Requirements**: Screen resolution ≥ 1920x1080
- **Left Pane (60% width)**: Displays 4:3 vertical, square, or 16:9 vertical photos
- **Right Pane (40% width)**: Displays 4:3 vertical, square, or 16:9 vertical photos
- **Best For**: High-resolution displays, showcasing two portrait photos side-by-side with flexible placement
- **Display Duration**: 15 seconds before rotating to next layout

### 🔄 Triple Pane Layout
- **Requirements**: Screen resolution ≥ 1920x1080
- **Left Pane**: Displays 16:9 vertical photos
- **Center Pane**: Displays 16:9 vertical photos
- **Right Pane**: Displays 16:9 vertical photos
- **Best For**: Ultra-wide displays, showcasing three tall portrait photos side-by-side
- **Display Duration**: 15 seconds before rotating to next layout

### 🎯 Quad Pane Layout (2x2 Grid)
- **Requirements**: Screen resolution ≥ 1920x1080
- **Top Left**: Square photos
- **Top Right**: 16:9 landscape photos
- **Bottom Left**: 4:3 vertical photos
- **Bottom Right**: 16:9 vertical photos
- **Best For**: High-resolution displays, showcasing four different photo types simultaneously
- **Display Duration**: 15 seconds before rotating to next layout

## 🚀 Layout Rotation System

The screen saver now features an **automatic layout rotation system** that:

- **🔄 Rotates Through Layouts**: Automatically cycles through all available layouts every 15 seconds
- **📱 Dynamic Experience**: Each layout shows new photos and rotates to the next layout simultaneously
- **⚙️ Configurable Timing**: Adjust rotation intervals via `config.txt`
- **🎯 Smart Fallback**: Automatically falls back to single pane if other layouts aren't supported
- **🔄 Seamless Transitions**: Smooth transitions between different layout modes

## Photo Classification System

The program automatically classifies photos into these aspect ratio categories:

| Aspect Ratio | Category Name | Description | Layout Usage |
|--------------|---------------|-------------|--------------|
| 21:9 | Ultra-Wide/Panoramic | Very wide landscape photos | Single pane only |
| 16:9 | 16:9 Landscape | Wide landscape photos | Single pane, Center pane, Top right pane |
| 9:16 | 16:9 Vertical | Tall portrait photos | Single pane, Both dual panes, All triple pane panes, Bottom right pane |
| 4:3 | 4:3 Landscape | Standard landscape photos | Single pane, Center pane |
| 3:4 | 4:3 Vertical | Standard portrait photos | Single pane, Both dual panes, Bottom left pane |
| 1:1 | Square | Square photos | Single pane, Both dual panes, Top left pane |

**Tolerance System**: Photos that are close to these ratios (within 20-30% tolerance) are automatically categorized. For example, a 3010x3000 photo will be classified as "Square" even though it's not exactly 1:1.

## Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux
- **For Multiple Layouts**: Screen resolution ≥ 1920x1080 (Full HD)
- **For Best Experience**: Screen resolution ≥ 2560x1440 (2K/QHD)

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your image folder and layout preferences:**
   Edit `config.txt` and set your preferences:
   ```
   IMAGE_FOLDER=C:\Users\YourName\Pictures\Screensaver
   LAYOUT_TYPE=auto  # or specific layout name
   LAYOUT_ROTATION_ENABLED=true
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Configuration

The `config.txt` file should contain:
```
# Screen Saver Configuration
# Path to the folder containing your images
IMAGE_FOLDER=C:\Users\YourName\Pictures\Screensaver

# Display settings
DISPLAY_INTERVAL=15000
FULLSCREEN=true

# Layout settings
LAYOUT_TYPE=auto
# Available layouts: auto, single_pane, dual_pane, triple_pane, quad_pane
# auto = automatically rotate through all available layouts
LAYOUT_ROTATION_ENABLED=true
PHOTO_LAYOUT_CHANGE_INTERVAL=15000
# How often both layout and photos change in milliseconds (15 seconds default)
```

**Important Notes:**
- Use forward slashes (/) or double backslashes (\\) in Windows paths
- The config file must be in the same directory as `main.py`
- If no config file exists, a default one will be created pointing to `~/Pictures/Screensaver`
- **Recursive Search**: The program will automatically find images in all subdirectories of the specified folder
- **Layout Selection**: The program will automatically fall back to single pane if other layouts are not supported by your screen resolution
- **Auto Mode**: Set `LAYOUT_TYPE=auto` for automatic layout rotation through all available layouts

## Usage

1. **Configure**: Edit `config.txt` with your image folder path and preferred layout mode
2. **Launch**: Run `python main.py`
3. **Enjoy**: The screen saver automatically starts displaying images with the selected layout behavior
4. **Exit**: Press any key, click anywhere, or press Escape to exit

## How the Slideshow Works

### 🎯 Auto Mode (Layout Rotation)
1. **Photo Discovery**: Recursively searches your folder for JPG, JPEG, and PNG files
2. **Classification**: Each photo is analyzed and categorized by aspect ratio
3. **Layout Rotation**: Automatically cycles through all available layouts every 15 seconds
4. **Photo Display**: Each layout shows appropriate photos for 15 seconds before rotating
5. **Continuous Experience**: Seamlessly transitions between different layout modes

### 📱 Specific Layout Mode
1. **Photo Discovery**: Same as auto mode
2. **Classification**: Same as auto mode
3. **Fixed Layout**: Uses the specified layout continuously
4. **Photo Rotation**: Photos rotate every 15 seconds within the same layout
5. **Static Experience**: Maintains the same layout throughout the session

## Controls

- **Any Key**: Exit screen saver
- **Mouse Click**: Exit screen saver  
- **Escape Key**: Exit screen saver

## Image Requirements

- **Supported Formats**: JPG, JPEG, PNG only
- **Aspect Ratio**: Images are stretched to completely fill their assigned pane dimensions
- **Screen Fit**: Images stretch to fill entire pane area (may distort but ensures no empty space)
- **Search Depth**: Images are found in the specified folder and all subdirectories

## Metadata Extraction

The program automatically extracts:
- **Width and Height**: Pixel dimensions from image files
- **Date Taken**: EXIF metadata if available, otherwise file modification time
- **Filename**: Original filename for reference

## Project Structure

The application is organized into modular components:

```
custom_photo_rotation/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── photo_classifier.py      # Aspect ratio classification logic
│   ├── photo_metadata.py        # Photo metadata extraction
│   ├── config_manager.py        # Configuration management
│   ├── layout_manager.py        # Layout system management
│   ├── photo_selector.py        # Photo selection for panes
│   ├── screensaver.py           # Main application logic
│   └── utils.py                 # Helper functions
├── main.py                      # Application entry point
├── config.txt                   # Configuration file
├── requirements.txt             # Dependencies
├── demo_layouts.py             # Layout system demonstration
└── README.md                    # Documentation
```

## Technical Details

- **Modular Architecture**: Clean separation of concerns with dedicated modules
- **Layout System**: Flexible layout management supporting multiple display modes
- **Layout Rotation**: Automatic cycling through different layouts with configurable timing
- **Smart Photo Placement**: Intelligent photo selection based on pane requirements
- Built with Python tkinter for the GUI
- Uses PIL (Pillow) for image processing and metadata extraction
- Automatic photo classification with configurable tolerance
- Category-based slideshow organization
- Recursive file search using `os.walk()` for comprehensive image discovery
- No UI elements - starts directly with slideshow

## Console Output

When running with auto layout rotation, you'll see detailed information:
```
Screen dimensions: 2560x1440
Configured layout type: auto
Layout rotation enabled with 4 layouts available
Available layouts: Single Pane, Dual Pane, Triple Pane, Quad Pane
Auto mode: Starting with layout: Single Pane

Layout Pane Summary:
  Main Pane (2560x1440): 214 photos
    Categories: ultra_wide, 16:9_landscape, 16:9_vertical, 4:3_landscape, 4:3_vertical, square

Layout rotation will occur every 30.0 seconds
Rotating to layout: Dual Pane

Layout Pane Summary:
  Left Pane (1536x1440): 13 photos
    Categories: 4:3_vertical, square
  Right Pane (1024x1440): 10 photos
    Categories: 4:3_vertical, 16:9_vertical
```

## Customization

### Layout Configuration
To change the layout behavior, modify the `config.txt` file:

```
# For automatic layout rotation (recommended)
LAYOUT_TYPE=auto

# For specific layout only
LAYOUT_TYPE=dual_pane

# Disable layout rotation
LAYOUT_ROTATION_ENABLED=false

# Adjust rotation timing (in milliseconds)
PHOTO_LAYOUT_CHANGE_INTERVAL=45000  # 45 seconds
```

### Photo Display Behavior
Photos are handled differently based on their aspect ratio category:

**✅ Ultra-Wide/Panoramic Photos (21:9):**
- **Maintain aspect ratio** to preserve their cinematic appearance
- **Letterboxed** with black bars to fit within pane boundaries
- Designed for wide screen viewing without distortion or cropping
- Entire photo content is visible

**✅ All Other Photo Types:**
- **Maintain aspect ratio** to preserve their natural appearance
- **Cropped to fill** their assigned pane dimensions completely
- Eliminates empty space without distorting the original aspect ratio
- Photos are scaled up to cover the pane, then center-cropped to fit exactly

**Layout-Specific Behavior:**
- **Single Pane**: All photos displayed appropriately for entire screen (2560×1440)
- **Dual Pane**:
  - Left pane (1536×1440): Ultra-wide letterboxed, others cropped to fill
  - Right pane (1024×1440): Ultra-wide letterboxed, others cropped to fill
- **Triple Pane**: Each pane (853×1440): Ultra-wide letterboxed, others cropped to fill

**Note**: Ultra-wide photos preserve their natural wide format with letterboxing, while standard photos use cropping for maximum screen utilization without distortion.

### Display Timing
To change the photo display interval within each layout:
```
# Change from 15 seconds to 10 seconds
DISPLAY_INTERVAL=10000
```

### Classification Tolerance
To adjust classification tolerance, modify the `tolerance` values in the `src/photo_classifier.py` file:
```python
'tolerance': 0.15  # 15% tolerance instead of 20%
```

## Debug Overlay System

The screen saver includes a debug overlay system that provides detailed information about photo selection and display.

### Debug Overlay Features

- **📊 Metadata Overlays**: Each photo displays a semi-transparent overlay showing:
  - **Pane**: Which pane the photo is displayed in
  - **File**: The filename of the photo
  - **Category**: The aspect ratio classification
  - **Original**: Original photo dimensions
  - **Display**: Pane display dimensions
  - **Category Error**: Difference from target aspect ratio
  - **Display Crop/Letterbox**: How much the photo is cropped or letterboxed
  - **Date**: When the photo was taken

- **⌨️ Manual Control**: 
  - **V Key**: Toggle debug overlay visibility on/off
  - **Enter Key**: Advance to the next layout/photo combination immediately
  - **Left Control**: Start issue reporting mode (timer pauses, photos stop changing)
  - **Left Control (again)**: Finish issue reporting and resume normal operation
  - **Escape**: Cancel issue reporting and resume normal operation
  - **Other Keys**: Exit the screen saver (normal behavior)

### Debug Overlay Usage

1. **Run the screen saver**:
   ```bash
   python main.py
   ```

2. **You'll see startup instructions**:
   ```
   🔍 Debug overlay controls:
      - Press 'v' to toggle debug overlay visibility
      - Press 'Enter' to manually advance to the next layout
      - Press 'Left Control' to start issue reporting (timer pauses)
      - Press 'Left Control' again to finish issue reporting (timer resumes)
      - Press 'Escape' or click to exit
   ```

3. **Test photo selection**:
   - Press **v** to show/hide debug overlays
   - Press **Enter** to manually advance through layouts
   - Press **Left Control** to start issue reporting (photos stop changing)
   - Type your issue description, then press **Left Control** again to finish
   - Watch the metadata overlays to verify classification
   - Observe layout rotation and pane assignments

### Debug Overlay Benefits

- **Photo Classification Verification**: Confirm photos are correctly categorized
- **Layout Testing**: Manually step through layouts to verify behavior
- **Pane Assignment Validation**: Ensure each pane gets appropriate photo types
- **Metadata Inspection**: Check dimensions, crop values, and aspect ratios
- **Issue Reporting**: Collect detailed issue descriptions with timestamps and pause photo rotation
- **Troubleshooting**: Identify issues with photo selection or layout rotation

### Comprehensive Logging System

The screen saver automatically creates detailed log files for debugging and monitoring:

#### **Log File Features:**
- **Automatic Creation**: Creates a `logs/` folder if it doesn't exist
- **Timestamped Filenames**: Each run creates a new log file with format `photo_rotation_YYYYMMDD_HHMMSS.log`
- **Dual Output**: All console output is simultaneously written to both console and log file
- **Complete Session Recording**: Captures everything from startup to shutdown
- **Issue Report Logging**: All issue reports and debug information are preserved
- **Error Tracking**: Exceptions and errors are logged with full context

#### **Log File Location:**
```
logs/
├── photo_rotation_20250821_230240.log
├── photo_rotation_20250821_231500.log
└── ...
```

#### **Log Content Includes:**
- Startup and shutdown timestamps
- Photo classification summaries
- Layout rotation events
- Photo selection details
- Debug overlay toggles
- Issue reporting sessions
- Error messages and exceptions
- Performance metrics

### Enhanced Issue Reporting

The screen saver includes an advanced issue reporting system that allows users to document problems in detail:

#### **How It Works:**
1. **Press Left Control** when you notice an issue - this pauses the photo rotation timer
2. **Type your description** of what went wrong (supports multi-line text)
3. **Press Left Control again** to finish and resume normal operation
4. **Press Escape** to cancel issue reporting and resume immediately

#### **Features:**
- **Timer Pause**: Photos stop changing while you're typing, preventing the issue from disappearing
- **Real-time Typing**: See your text as you type with live feedback
- **Multi-line Support**: Use Enter key for line breaks in your description
- **Duration Tracking**: Records how long you spent documenting the issue
- **Context Preservation**: Captures current layout and debug overlay state
- **Comprehensive Logging**: All issue reports are saved with timestamps and descriptions

#### **Example Issue Report:**
```
================================================================================
🚩 ISSUE REPORT COMPLETED - 2025-08-21 21:46:58.917
   Duration: 12.34 seconds
   Issue Description:
     Photo IMG_1234.jpg appeared twice in the same layout
     This happened during the Dual Pane layout
     The photo was shown in both left and right panes
================================================================================
```

### Default State

Debug overlays are **hidden by default** and can be toggled on/off as needed during operation.

## Troubleshooting

- **No Images Display**: Check that your `config.txt` file has the correct path
- **Folder Not Found**: Verify the folder path exists and is accessible
- **No Supported Images**: Ensure your folder contains JPG, JPEG, or PNG files
- **Layout Not Available**: Check that your screen resolution meets the minimum requirements (≥1920x1080)
- **Layout Rotation Issues**: Verify `LAYOUT_ROTATION_ENABLED=true` and check `PHOTO_LAYOUT_CHANGE_INTERVAL` settings
- **Photo Classification Issues**: Press **v** to toggle debug overlays and verify photo categorization
- **Performance Issues**: Large images may take longer to load; consider resizing them beforehand
- **Exit Issues**: Use Ctrl+C in the terminal if the application becomes unresponsive
- **Log File Issues**: Check the `logs/` folder for detailed error information and session history

## Example Config File

```
# Screen Saver Configuration
# Path to the folder containing your images
IMAGE_FOLDER=C:\Users\Aaron\Pictures\Vacation Photos

# Display settings
DISPLAY_INTERVAL=15000
FULLSCREEN=true

# Layout settings
LAYOUT_TYPE=auto
LAYOUT_ROTATION_ENABLED=true
PHOTO_LAYOUT_CHANGE_INTERVAL=15000


```

**Note**: This will find all images in "Vacation Photos" and any subfolders, classify them by aspect ratio, and automatically rotate through all available layouts every 15 seconds, with each layout displaying appropriate photos for 15 seconds.

## Demo and Testing

Run the layout demonstration script to see all available layouts:
```bash
python demo_layouts.py
```

This will show:
- Available layouts for different screen resolutions
- Layout rotation capabilities
- Photo organization across different layouts
- Configuration options

## License

This project is open source and available under the MIT License.
