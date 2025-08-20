# Custom Photo Rotation Screen Saver

A Python-based screen saver application that displays images from a configured folder with automatic rotation every 15 seconds. The program recursively searches for images in all subdirectories and classifies them by aspect ratio for organized slideshow presentation.

## Features

- **Fullscreen Display**: Runs in fullscreen mode for true screen saver experience
- **Smart Aspect Ratio Handling**: Automatically resizes images to fit screen while maintaining their original aspect ratio
- **15-Second Intervals**: Each image is displayed for exactly 15 seconds
- **Photo Classification**: Automatically categorizes photos into 5 aspect ratio categories
- **Metadata Extraction**: Extracts width, height, and date taken from photos
- **Multiple Formats**: Supports JPG, JPEG, and PNG formats
- **Easy Exit**: Press any key, click, or press Escape to exit
- **Config File**: Simple text file configuration for image folder path
- **Recursive Search**: Automatically finds images in all subdirectories
- **Organized Slideshow**: Photos are grouped by category and displayed sequentially

## Photo Classification System

The program automatically classifies photos into these aspect ratio categories:

| Aspect Ratio | Category Name | Description |
|--------------|---------------|-------------|
| 16:9 | 16:9 Landscape | Wide landscape photos |
| 9:16 | 16:9 Vertical | Tall portrait photos |
| 4:3 | 4:3 Landscape | Standard landscape photos |
| 3:4 | 4:3 Vertical | Standard portrait photos |
| 1:1 | Square | Square photos |

**Tolerance System**: Photos that are close to these ratios (within 10% tolerance) are automatically categorized. For example, a 3010x3000 photo will be classified as "Square" even though it's not exactly 1:1.

## Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your image folder:**
   Edit `config.txt` and set your image folder path:
   ```
   IMAGE_FOLDER=C:\Users\YourName\Pictures\Screensaver
   ```

3. **Run the application:**
   ```bash
   python screensaver.py
   ```

## Configuration

The `config.txt` file should contain:
```
# Screen Saver Configuration
# Path to the folder containing your images
IMAGE_FOLDER=C:\Users\YourName\Pictures\Screensaver
```

**Important Notes:**
- Use forward slashes (/) or double backslashes (\\) in Windows paths
- The config file must be in the same directory as `screensaver.py`
- If no config file exists, a default one will be created pointing to `~/Pictures/Screensaver`
- **Recursive Search**: The program will automatically find images in all subdirectories of the specified folder

## Usage

1. **Configure**: Edit `config.txt` with your image folder path
2. **Launch**: Run `python screensaver.py`
3. **Enjoy**: The screen saver automatically starts displaying images in 15-second intervals
4. **Exit**: Press any key, click anywhere, or press Escape to exit

## How the Slideshow Works

1. **Photo Discovery**: Recursively searches your folder for JPG, JPEG, and PNG files
2. **Classification**: Each photo is analyzed and categorized by aspect ratio
3. **Organization**: Photos are grouped by category (16:9 Landscape, Square, etc.)
4. **Sequential Display**: Shows all photos in one category before moving to the next
5. **Continuous Loop**: Cycles through all categories and photos indefinitely

## Controls

- **Any Key**: Exit screen saver
- **Mouse Click**: Exit screen saver  
- **Escape Key**: Exit screen saver

## Image Requirements

- **Supported Formats**: JPG, JPEG, PNG only
- **Aspect Ratio**: Images maintain their original aspect ratio when displayed
- **Screen Fit**: Images are scaled to fit your screen while preserving proportions
- **Search Depth**: Images are found in the specified folder and all subdirectories

## Metadata Extraction

The program automatically extracts:
- **Width and Height**: Pixel dimensions from image files
- **Date Taken**: EXIF metadata if available, otherwise file modification time
- **Filename**: Original filename for reference

## Technical Details

- Built with Python tkinter for the GUI
- Uses PIL (Pillow) for image processing and metadata extraction
- Automatic photo classification with configurable tolerance
- Category-based slideshow organization
- Recursive file search using `os.walk()` for comprehensive image discovery
- No UI elements - starts directly with slideshow

## Console Output

When running, you'll see detailed information:
```
Loading and classifying photos from: C:\Users\Aaron\Pictures\Vacation Photos

Photo Classification Summary:
Total photos found: 137
  16:9 Landscape: 45 photos
  4:3 Landscape: 32 photos
  Square: 28 photos
  16:9 Vertical: 20 photos
  4:3 Vertical: 12 photos

Switching to category: 16:9 Landscape (45 photos)
```

## Customization

To change the display interval, modify the `15000` value (in milliseconds) in the `show_next_photo` method:

```python
# Change from 15 seconds to 10 seconds
self.root.after(10000, self.next_photo)  # 10 seconds
```

To adjust classification tolerance, modify the `tolerance` values in the `PhotoClassifier` class:

```python
'tolerance': 0.15  # 15% tolerance instead of 10%
```

## Troubleshooting

- **No Images Display**: Check that your `config.txt` file has the correct path
- **Folder Not Found**: Verify the folder path exists and is accessible
- **No Supported Images**: Ensure your folder contains JPG, JPEG, or PNG files
- **Performance Issues**: Large images may take longer to load; consider resizing them beforehand
- **Exit Issues**: Use Ctrl+C in the terminal if the application becomes unresponsive

## Example Config File

```
# Screen Saver Configuration
# Path to the folder containing your images
IMAGE_FOLDER=C:\Users\Aaron\Pictures\Vacation Photos
```

**Note**: This will find all images in "Vacation Photos" and any subfolders, classify them by aspect ratio, and display them in organized categories.

## License

This project is open source and available under the MIT License.
