"""
Configuration management module for the screen saver.
"""

import os


class ConfigManager:
    """Manages configuration file operations"""
    
    def __init__(self, config_file="config.txt"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('#') or not line:
                            continue
                        
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Remove quotes if present
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            
                            self.config[key] = value
            else:
                # Create default config if it doesn't exist
                self.create_default_config()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create a default configuration file"""
        try:
            default_folder = os.path.expanduser("~/Pictures/Screensaver")
            
            config_content = [
                "# Screen Saver Configuration",
                "# Path to the folder containing your images",
                f"IMAGE_FOLDER={default_folder}",
                "",
                "# Display settings",
                "DISPLAY_INTERVAL=15000",
                "FULLSCREEN=true",
                "",
                "# Layout settings",
                "LAYOUT_TYPE=auto",
                "# Available layouts: auto, single_pane, dual_pane, triple_pane, quad_pane",
                "# auto = automatically rotate through all available layouts",
                "LAYOUT_ROTATION_ENABLED=true",
                "LAYOUT_ROTATION_INTERVAL=30000",
                "# Layout rotation interval in milliseconds (30 seconds default)",
                "",
                "# Debug settings",
                "DEBUG_MODE=false",
                "# Enable debug mode to show metadata overlays on photos"
            ]
            
            with open(self.config_file, 'w') as f:
                f.write('\n'.join(config_content))
            
            # Set default values
            self.config['IMAGE_FOLDER'] = default_folder
            self.config['DISPLAY_INTERVAL'] = '15000'
            self.config['FULLSCREEN'] = 'true'
            self.config['LAYOUT_TYPE'] = 'auto'
            self.config['LAYOUT_ROTATION_ENABLED'] = 'true'
            self.config['LAYOUT_ROTATION_INTERVAL'] = '30000'
            self.config['DEBUG_MODE'] = 'false'
            
            print(f"Created default config file: {self.config_file}")
            
        except Exception as e:
            print(f"Error creating default config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = str(value)
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                f.write(f"# Path to the folder containing your images\n")
                f.write(f"IMAGE_FOLDER={self.config.get('IMAGE_FOLDER', '')}\n")
                f.write("\n")
                f.write(f"# Display settings\n")
                f.write(f"DISPLAY_INTERVAL={self.config.get('DISPLAY_INTERVAL', '15000')}\n")
                f.write(f"FULLSCREEN={self.config.get('FULLSCREEN', 'true')}\n")
                f.write("\n")
                f.write(f"# Layout settings\n")
                f.write(f"LAYOUT_TYPE={self.config.get('LAYOUT_TYPE', 'auto')}\n")
                f.write("# Available layouts: auto, single_pane, dual_pane, triple_pane, quad_pane\n")
                f.write("# auto = automatically rotate through all available layouts\n")
                f.write(f"LAYOUT_ROTATION_ENABLED={self.config.get('LAYOUT_ROTATION_ENABLED', 'true')}\n")
                f.write(f"LAYOUT_ROTATION_INTERVAL={self.config.get('LAYOUT_ROTATION_INTERVAL', '30000')}\n")
                f.write("# Layout rotation interval in milliseconds (30 seconds default)\n")
                f.write("\n")
                f.write(f"# Debug settings\n")
                f.write(f"DEBUG_MODE={self.config.get('DEBUG_MODE', 'false')}\n")
                f.write("# Enable debug mode to show metadata overlays on photos\n")
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_image_folder(self):
        """Get the configured image folder path"""
        return self.config.get('IMAGE_FOLDER', '')
    
    def set_image_folder(self, folder_path):
        """Set the image folder path"""
        self.set('IMAGE_FOLDER', folder_path)
    
    def get_display_interval(self):
        """Get the display interval in milliseconds"""
        try:
            return int(self.config.get('DISPLAY_INTERVAL', '15000'))
        except ValueError:
            return 15000
    
    def is_fullscreen(self):
        """Check if fullscreen mode is enabled"""
        return self.config.get('FULLSCREEN', 'true').lower() == 'true'
    
    def get_layout_type(self):
        """Get the configured layout type"""
        return self.config.get('LAYOUT_TYPE', 'auto')
    
    def set_layout_type(self, layout_type):
        """Set the layout type"""
        self.set('LAYOUT_TYPE', layout_type)
    
    def is_layout_rotation_enabled(self):
        """Check if layout rotation is enabled"""
        return self.config.get('LAYOUT_ROTATION_ENABLED', 'true').lower() == 'true'
    
    def set_layout_rotation_enabled(self, enabled):
        """Enable or disable layout rotation"""
        self.set('LAYOUT_ROTATION_ENABLED', str(enabled).lower())
    
    def get_layout_rotation_interval(self):
        """Get the layout rotation interval in milliseconds"""
        try:
            return int(self.config.get('LAYOUT_ROTATION_INTERVAL', '30000'))
        except ValueError:
            return 30000
    
    def set_layout_rotation_interval(self, interval):
        """Set the layout rotation interval in milliseconds"""
        self.set('LAYOUT_ROTATION_INTERVAL', str(interval))
    
    def is_debug_mode_enabled(self):
        """Check if debug mode is enabled"""
        return self.config.get('DEBUG_MODE', 'false').lower() == 'true'
    
    def set_debug_mode_enabled(self, enabled):
        """Enable or disable debug mode"""
        self.set('DEBUG_MODE', str(enabled).lower())
    
    def validate_image_folder(self):
        """Validate that the configured image folder exists"""
        folder = self.get_image_folder()
        if not folder:
            return False, "No image folder configured"
        
        if not os.path.exists(folder):
            return False, f"Image folder not found: {folder}"
        
        if not os.path.isdir(folder):
            return False, f"Path is not a directory: {folder}"
        
        return True, "Valid"
