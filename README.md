# Custom Photo Rotation Screen Saver

A Python-based screen saver application that displays images from a configured folder with automatic rotation every 15 seconds. The program recursively searches for images in all subdirectories.

## Features

- **Fullscreen Display**: Runs in fullscreen mode for true screen saver experience
- **16:9 Aspect Ratio**: Automatically resizes images to maintain 16:9 aspect ratio
- **15-Second Intervals**: Each image is displayed for exactly 15 seconds
- **Multiple Formats**: Supports JPG, JPEG, PNG, BMP, GIF, and TIFF formats
- **Easy Exit**: Press any key, click, or press Escape to exit
- **Config File**: Simple text file configuration for image folder path
- **Recursive Search**: Automatically finds images in all subdirectories

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

## Controls

- **Any Key**: Exit screen saver
- **Mouse Click**: Exit screen saver  
- **Escape Key**: Exit screen saver

## Image Requirements

- **Supported Formats**: JPG, JPEG, PNG, BMP, GIF, TIFF
- **Aspect Ratio**: Images will be automatically resized to fit 16:9 ratio
- **Screen Fit**: Images are scaled to fit your screen while maintaining aspect ratio
- **Search Depth**: Images are found in the specified folder and all subdirectories

## Technical Details

- Built with Python tkinter for the GUI
- Uses PIL (Pillow) for image processing
- Automatic image rotation with configurable timing
- Responsive design that adapts to different screen resolutions
- No UI elements - starts directly with slideshow
- **Recursive file search** using `os.walk()` for comprehensive image discovery

## Customization

To change the display interval, modify the `15000` value (in milliseconds) in the `show_next_image` method:

```python
# Change from 15 seconds to 10 seconds
self.root.after(10000, self.next_image)  # 10 seconds
```

## Troubleshooting

- **No Images Display**: Check that your `config.txt` file has the correct path
- **Folder Not Found**: Verify the folder path exists and is accessible
- **No Supported Images**: Ensure your folder contains JPG, PNG, BMP, GIF, or TIFF files
- **Performance Issues**: Large images may take longer to load; consider resizing them beforehand
- **Exit Issues**: Use Ctrl+C in the terminal if the application becomes unresponsive

## Example Config File

```
# Screen Saver Configuration
# Path to the folder containing your images
IMAGE_FOLDER=C:\Users\Aaron\Pictures\Vacation Photos
```

**Note**: This will find all images in "Vacation Photos" and any subfolders like "Vacation Photos\Beach", "Vacation Photos\Mountains", etc.

## License

This project is open source and available under the MIT License.
