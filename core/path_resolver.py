"""
Path resolver for PyInstaller compatibility.

When the app is bundled with PyInstaller, __file__ based paths point inside
the temporary extraction folder. This module provides a consistent way to
resolve paths whether running from source or from a frozen .exe.

- get_app_dir()     -> The directory where the .exe (or main.py) lives.
                       Used for user-writable files: database, logs, output PDFs.
- get_resource_path(relative) -> Resolves a path to a bundled resource file.
                       Points into the PyInstaller _MEIPASS temp folder when frozen,
                       or to the project root when running from source.
"""

import sys
import os


def is_frozen() -> bool:
    """Check if we are running inside a PyInstaller bundle."""
    return getattr(sys, 'frozen', False)


def get_app_dir() -> str:
    """
    Get the directory where the application executable (or main.py) resides.
    
    This is the correct base path for user-writable files like the database,
    log directory, and output folders. It stays consistent across runs.
    """
    if is_frozen():
        # sys.executable is the path to the .exe
        return os.path.dirname(sys.executable)
    else:
        # Running from source: project root is parent of this file's directory (core/)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a bundled resource file.
    
    When frozen, PyInstaller extracts bundled data files to a temp folder
    referenced by sys._MEIPASS. When running from source, this just resolves
    relative to the project root.
    
    Args:
        relative_path: Path relative to the project root (e.g., 'logo.png')
    
    Returns:
        Absolute path to the resource.
    """
    if is_frozen():
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
