"""
Logging module for the photo rotation screensaver.
Handles both console and file logging with timestamped filenames.
"""

import os
import sys
from datetime import datetime
from typing import TextIO


class Logger:
    """Handles logging to both console and file with timestamped filenames"""
    
    def __init__(self, log_folder: str = "logs"):
        self.log_folder = log_folder
        self.log_file = None
        self.log_file_path = None
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Create log folder if it doesn't exist
        self._ensure_log_folder_exists()
        
        # Create timestamped log file
        self._create_log_file()
        
        # Redirect stdout and stderr to both console and file
        self._setup_dual_output()
    
    def _ensure_log_folder_exists(self):
        """Create the log folder if it doesn't exist"""
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
            print(f"📁 Created log folder: {self.log_folder}")
    
    def _create_log_file(self):
        """Create a new log file with timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_rotation_{timestamp}.log"
        self.log_file_path = os.path.join(self.log_folder, filename)
        
        try:
            self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
            print(f"📝 Logging to file: {self.log_file_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create log file: {e}")
            self.log_file = None
    
    def _setup_dual_output(self):
        """Setup dual output to both console and file"""
        if self.log_file:
            # Create a custom stdout that writes to both console and file
            class DualOutput:
                def __init__(self, console_stream, file_stream):
                    self.console_stream = console_stream
                    self.file_stream = file_stream
                
                def write(self, text):
                    # Safely write to console stream (handle None case)
                    if self.console_stream and hasattr(self.console_stream, 'write'):
                        try:
                            self.console_stream.write(text)
                            self.console_stream.flush()
                        except (AttributeError, OSError):
                            pass  # Console stream unavailable
                    
                    # Always write to file stream
                    if self.file_stream and not self.file_stream.closed:
                        try:
                            self.file_stream.write(text)
                            self.file_stream.flush()
                        except Exception:
                            pass
                
                def flush(self):
                    # Safely flush console stream
                    if self.console_stream and hasattr(self.console_stream, 'flush'):
                        try:
                            self.console_stream.flush()
                        except (AttributeError, OSError):
                            pass
                    
                    # Always flush file stream
                    if self.file_stream and not self.file_stream.closed:
                        try:
                            self.file_stream.flush()
                        except Exception:
                            pass
            
            # Check if stdout/stderr are available before setting up dual output
            if self.original_stdout and hasattr(self.original_stdout, 'write'):
                sys.stdout = DualOutput(self.original_stdout, self.log_file)
            else:
                # Fallback: just write to file
                sys.stdout = DualOutput(None, self.log_file)
            
            if self.original_stderr and hasattr(self.original_stderr, 'write'):
                sys.stderr = DualOutput(self.original_stderr, self.log_file)
            else:
                # Fallback: just write to file
                sys.stderr = DualOutput(None, self.log_file)
    
    def close(self):
        """Close the log file and restore original stdout/stderr"""
        if self.log_file and not self.log_file.closed:
            self.log_file.close()
        
        # Restore original streams only if they're valid
        if self.original_stdout and hasattr(self.original_stdout, 'write'):
            sys.stdout = self.original_stdout
        if self.original_stderr and hasattr(self.original_stderr, 'write'):
            sys.stderr = self.original_stderr
        
        if self.log_file_path:
            print(f"📝 Log file saved: {self.log_file_path}")
    
    def get_log_file_path(self) -> str:
        """Get the current log file path"""
        return self.log_file_path or ""


# Global logger instance
_logger = None


def get_logger() -> Logger:
    """Get the global logger instance"""
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger


def close_logger():
    """Close the global logger"""
    global _logger
    if _logger:
        _logger.close()
        _logger = None


def log_startup():
    """Log startup information"""
    logger = get_logger()
    if logger.log_file:
        print(f"🚀 Photo Rotation Screensaver Started")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Log folder: {logger.log_folder}")
        print(f"📝 Log file: {os.path.basename(logger.log_file_path)}")
        print("=" * 60)


def log_shutdown():
    """Log shutdown information"""
    logger = get_logger()
    if logger.log_file:
        print("=" * 60)
        print(f"🛑 Photo Rotation Screensaver Shutting Down")
        print(f"📅 Ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Log file: {os.path.basename(logger.log_file_path)}")
        print(f"📁 Full log path: {logger.log_file_path}")
