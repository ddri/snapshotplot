"""
Utility functions for snapshotplot.

This module contains miscellaneous helper functions used throughout the package.
"""

import matplotlib.pyplot as plt
from typing import Optional, Any
import warnings


def save_current_plot(filepath: str, dpi: int = 300, bbox_inches: str = 'tight') -> None:
    """
    Save the current matplotlib figure to a file.
    
    Args:
        filepath: Path where to save the plot
        dpi: DPI for the saved image
        bbox_inches: Bounding box setting for the plot
    """
    try:
        # Get the current figure
        fig = plt.gcf()
        
        if fig is None or len(fig.axes) == 0:
            warnings.warn("No matplotlib figure found to save")
            return
        
        # Save the figure
        fig.savefig(
            filepath,
            dpi=dpi,
            bbox_inches=bbox_inches,
            facecolor='white',
            edgecolor='none'
        )
        
    except Exception as e:
        warnings.warn(f"Failed to save plot to {filepath}: {e}")


def has_active_figure() -> bool:
    """
    Check if there's an active matplotlib figure with content.
    
    Returns:
        bool: True if there's an active figure with axes
    """
    try:
        fig = plt.gcf()
        return fig is not None and len(fig.axes) > 0
    except Exception:
        return False


def clear_figure() -> None:
    """
    Clear the current matplotlib figure.
    """
    try:
        plt.clf()
    except Exception:
        pass


def format_timestamp_for_display(timestamp: str) -> str:
    """
    Format a timestamp for human-readable display.
    
    Args:
        timestamp: Timestamp in format YYYYMMDD_HHMMSS_microseconds
        
    Returns:
        str: Formatted timestamp
    """
    try:
        # Parse the timestamp
        date_part = timestamp[:8]  # YYYYMMDD
        time_part = timestamp[9:15]  # HHMMSS
        
        year = date_part[:4]
        month = date_part[4:6]
        day = date_part[6:8]
        
        hour = time_part[:2]
        minute = time_part[2:4]
        second = time_part[4:6]
        
        return f"{year}-{month}-{day} {hour}:{minute}:{second} UTC"
    except Exception:
        return timestamp


def validate_config(config: dict) -> dict:
    """
    Validate and sanitize configuration parameters.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        dict: Validated configuration
    """
    validated = config.copy()
    
    # Validate output_dir
    if 'output_dir' in validated:
        if not isinstance(validated['output_dir'], str):
            validated['output_dir'] = 'snapshots'
    
    # Validate title
    if 'title' in validated:
        if not isinstance(validated['title'], str):
            validated['title'] = None
    
    # Validate author
    if 'author' in validated:
        if not isinstance(validated['author'], str):
            validated['author'] = None
    
    # Validate notes
    if 'notes' in validated:
        if not isinstance(validated['notes'], str):
            validated['notes'] = None
    
    return validated


def get_default_config() -> dict:
    """
    Get default configuration values.
    
    Returns:
        dict: Default configuration
    """
    return {
        'output_dir': 'snapshots',
        'title': None,
        'author': None,
        'notes': None,
        'dpi': 300,
        'bbox_inches': 'tight'
    }


def merge_configs(default: dict, user: dict) -> dict:
    """
    Merge user configuration with defaults.
    
    Args:
        default: Default configuration
        user: User-provided configuration
        
    Returns:
        dict: Merged configuration
    """
    merged = default.copy()
    
    if user:
        for key, value in user.items():
            if value is not None:  # Only override if user provided a value
                merged[key] = value
    
    return merged


def safe_filename(filename: str) -> str:
    """
    Make a filename safe for filesystem operations.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    import re
    
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure it's not empty
    if not filename:
        filename = 'unnamed'
    
    return filename


def get_python_version() -> str:
    """
    Get the current Python version as a string.
    
    Returns:
        str: Python version
    """
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def is_matplotlib_available() -> bool:
    """
    Check if matplotlib is available and working.
    
    Returns:
        bool: True if matplotlib is available
    """
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        return True
    except ImportError:
        return False


def get_matplotlib_version() -> Optional[str]:
    """
    Get matplotlib version if available.
    
    Returns:
        Optional[str]: Matplotlib version or None
    """
    try:
        import matplotlib
        return matplotlib.__version__
    except ImportError:
        return None 