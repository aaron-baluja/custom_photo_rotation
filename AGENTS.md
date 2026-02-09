# Codebase Structure Guide (For Future Agents)

This repo is a Python/Tkinter screensaver that rotates photos in multiple pane layouts. Use this as a quick map to where things live and how data flows.

## Top-Level Map
- `main.py`: App entry point. Sets up logging, loads config, starts the screensaver.
- `src/`: Core application modules (screensaver, layout logic, photo selection, metadata, etc.).
- `config.txt`: User configuration (image folder, rotation interval, layout type, weights).
- `build_distribution.py`: Builds a standalone Windows executable via PyInstaller and packages it.
- `README.md`, `User_Guide.txt`: High-level user docs.
- `tests/`: Tests (minimal; check what exists before relying on coverage).

## Runtime Flow (High-Level)
1. `main.py` adds `src/` to `sys.path`, initializes logging, loads config, then instantiates `ScreenSaver`.
2. `ScreenSaver` (`src/screensaver.py`) creates a fullscreen Tkinter window and initializes:
   - `ConfigManager` (reads config)
   - `PhotoClassifier` (aspect ratio categories)
   - `LayoutManager` (available layouts based on screen size)
   - `PhotoSelector` (picks photos per pane)
3. It scans `IMAGE_FOLDER` recursively, builds `PhotoMetadata` for each image, and classifies them.
4. It picks a layout (or a specific layout if configured) and selects photos per pane.
5. A timer rotates layouts/photos on the configured interval.

## Core Modules (What to Read First)
- `src/screensaver.py`: The "orchestrator." Fullscreen window, timers, input handling, and display rendering live here.
- `src/layout_manager.py`: Defines pane layouts and weighted layout selection.
- `src/photo_selector.py`: Photo selection logic including repetition reduction, seasonal/time weighting, and crop validation.
- `src/photo_metadata.py`: Reads file size, dimensions, and EXIF date (fallback to file mtime).
- `src/photo_classifier.py`: Aspect ratio classification with tolerances.
- `src/config_manager.py`: Config file parsing and defaults.
- `src/utils.py`: File scanning and display/crop calculations.
- `src/logger.py`: Dual console+file logging.

## Layouts
Layouts are defined in `src/layout_manager.py` and vary by screen size:
- Single, dual, triple vertical
- Multi-pane grids (Three Mixed, Four/Five/Six Photos)
Layouts have weights; optional config overrides are parsed from `LAYOUT_WEIGHTS`.

## Photo Selection Rules (In `src/photo_selector.py`)
- Avoid repeats within a layout and across categories until exhausted.
- Apply time weighting (photos within +/- 7 days of today are more likely).
- Reject (or retry) layouts with excessive cropping; ultra-wide images are letterboxed.

## Configuration
Default config keys read in `src/config_manager.py`:
- `IMAGE_FOLDER`: Root folder for images (recursive scan).
- `CHANGE_INTERVAL`: Rotation interval in ms.
- `LAYOUT_TYPE`: `auto` or a specific layout name.
- `LAYOUT_WEIGHTS`: Optional weights per layout (see parsing in config manager).
- `TIME_WEIGHTING_MULTIPLIER`: Multiplier for seasonal photo weighting.

Config is looked up in the current working directory first, then in PyInstaller bundle resources.

## Tests
There is no formal automated test suite. The repo includes a small sanity check script:
- `python test_three_mixed.py` (verifies the "Three Mixed Photos" layout is defined correctly)

## Run The Program
From the repo root:
- `python main.py`

Optional:
- `python demo_layouts.py` (renders layout previews)
- `run_screensaver.bat` (Windows helper to launch the screensaver)

## Build / Distribution
`build_distribution.py`:
- Cleans `build/` and `dist/`
- Runs PyInstaller
- Creates helper files and a template `config.txt`
- Zips the `dist/` output into `distributions/`
Run it with:
- `python build_distribution.py`

## Logs and Output
Logs go to `logs/` with timestamped filenames. `src/logger.py` redirects stdout/stderr to both console and log file.
Log filenames follow `photo_rotation_YYYYMMDD_HHMMSS.log`.

## Quick Pointers For Changes
- UI behavior or key controls: `src/screensaver.py`
- Add/adjust layouts: `src/layout_manager.py`
- Photo selection strategy: `src/photo_selector.py`
- Config changes: `src/config_manager.py` + `config.txt` template
