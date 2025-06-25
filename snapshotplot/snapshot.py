"""
Core snapshot functionality for snapshotplot.

This module provides the main decorator and context manager for capturing
Python code, matplotlib plots, and generating HTML documentation.
"""

import functools
import os
from typing import Optional, Callable, Any, Dict, Union
from contextlib import contextmanager

from .timestamp import get_timestamp, get_datetime, reset_timestamp, generate_new_timestamp
from .code_capture import get_calling_info
from .file_manager import (
    create_output_directory, 
    get_file_paths, 
    get_default_output_dir,
    sanitize_filename
)
from .html_writer import create_html_snapshot
from .utils import (
    save_current_plot, 
    has_active_figure, 
    get_default_config, 
    merge_configs,
    validate_config,
    format_timestamp_for_display
)


class SnapshotContext:
    """Context manager for snapshot functionality."""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        notes: Optional[str] = None,
        dpi: int = 300,
        bbox_inches: str = 'tight'
    ):
        """
        Initialize the snapshot context manager.
        
        Args:
            output_dir: Directory to save snapshots (default: 'snapshots')
            title: Custom title for the HTML output
            author: Author name for metadata
            notes: Additional notes for the snapshot
            dpi: DPI for saved plots
            bbox_inches: Bounding box setting for plots
        """
        self.config = {
            'output_dir': output_dir,
            'title': title,
            'author': author,
            'notes': notes,
            'dpi': dpi,
            'bbox_inches': bbox_inches
        }
        
        # Validate and merge with defaults
        default_config = get_default_config()
        self.config = merge_configs(default_config, validate_config(self.config))
        
        # Initialize state
        self.timestamp = None
        self.calling_info = None
        self.file_paths = None
        
    def __enter__(self):
        """Enter the context and prepare for snapshot capture."""
        # Use the global timestamp for this snapshot run
        from .timestamp import get_timestamp
        self.timestamp = get_timestamp()
        
        # Get calling information
        self.calling_info = get_calling_info(depth=3)
        
        # Set up output directory and file paths
        output_dir = self.config['output_dir'] or get_default_output_dir()
        snapshot_dir = create_output_directory(
            output_dir, 
            self.calling_info['filename']
        )
        
        self.file_paths = get_file_paths(
            snapshot_dir,
            self.calling_info['filename'],
            self.timestamp
        )
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and create the snapshot."""
        try:
            self._create_snapshot()
        except Exception as e:
            # Don't let snapshot errors interfere with the main code
            import warnings
            warnings.warn(f"Snapshot creation failed: {e}")
    
    def _create_snapshot(self):
        """Create the complete snapshot with all components."""
        if not self.calling_info or not self.file_paths:
            return
        
        # Save source code
        self._save_source_code()
        
        # Save plot if available
        plot_saved = self._save_plot()
        
        # Create HTML documentation
        self._create_html_documentation(plot_saved)
    
    def _save_source_code(self):
        """Save the source code to a file."""
        try:
            with open(self.file_paths['code'], 'w', encoding='utf-8') as f:
                f.write(self.calling_info['source_code'])
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to save source code: {e}")
    
    def _save_plot(self) -> bool:
        """Save the current matplotlib plot if available."""
        if not has_active_figure():
            return False
        
        try:
            save_current_plot(
                self.file_paths['plot'],
                dpi=self.config['dpi'],
                bbox_inches=self.config['bbox_inches']
            )
            return True
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to save plot: {e}")
            return False
    
    def _create_html_documentation(self, plot_saved: bool):
        """Create HTML documentation for the snapshot."""
        try:
            # Prepare metadata
            metadata = {
                'function_name': self.calling_info['function_name'],
                'filename': self.calling_info['filename'],
                'date': format_timestamp_for_display(self.timestamp)
            }
            
            # Always create HTML snapshot, even if no plot
            plot_path = self.file_paths['plot'] if plot_saved else ''
            create_html_snapshot(
                code=self.calling_info['source_code'],
                plot_path=plot_path,
                html_path=self.file_paths['html'],
                metadata=metadata,
                title=self.config['title'],
                author=self.config['author'],
                notes=self.config['notes']
            )
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to create HTML documentation: {e}")


class SnapshotDecorator:
    """Decorator class that can also be used as a context manager."""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        notes: Optional[str] = None,
        dpi: int = 300,
        bbox_inches: str = 'tight'
    ):
        """Initialize the decorator with configuration."""
        self.config = {
            'output_dir': output_dir,
            'title': title,
            'author': author,
            'notes': notes,
            'dpi': dpi,
            'bbox_inches': bbox_inches
        }
    
    def __call__(self, func: Callable) -> Callable:
        """Use as a decorator."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create snapshot context
            with SnapshotContext(**self.config):
                # Execute the function
                result = func(*args, **kwargs)
                return result
        
        return wrapper
    
    def __enter__(self):
        """Use as a context manager."""
        self.context = SnapshotContext(**self.config)
        return self.context.__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        return self.context.__exit__(exc_type, exc_val, exc_tb)


def snapshot(
    output_dir: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    notes: Optional[str] = None,
    dpi: int = 300,
    bbox_inches: str = 'tight'
) -> Union[SnapshotDecorator, Callable]:
    """
    Create a snapshot decorator or context manager.
    
    This function can be used in two ways:
    
    1. As a decorator:
        @snapshot()
        def my_function():
            # code here
    
    2. As a context manager:
        with snapshot():
            # code here
    
    Args:
        output_dir: Directory to save snapshots (default: 'snapshots')
        title: Custom title for the HTML output
        author: Author name for metadata
        notes: Additional notes for the snapshot
        dpi: DPI for saved plots
        bbox_inches: Bounding box setting for plots
        
    Returns:
        SnapshotDecorator: Can be used as decorator or context manager
    """
    return SnapshotDecorator(
        output_dir=output_dir,
        title=title,
        author=author,
        notes=notes,
        dpi=dpi,
        bbox_inches=bbox_inches
    )


# Convenience function for direct usage
def create_snapshot(
    output_dir: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    notes: Optional[str] = None,
    dpi: int = 300,
    bbox_inches: str = 'tight'
) -> SnapshotContext:
    """
    Create a snapshot context manager with the given configuration.
    
    Args:
        output_dir: Directory to save snapshots (default: 'snapshots')
        title: Custom title for the HTML output
        author: Author name for metadata
        notes: Additional notes for the snapshot
        dpi: DPI for saved plots
        bbox_inches: Bounding box setting for plots
        
    Returns:
        SnapshotContext: Configured context manager
    """
    return SnapshotContext(
        output_dir=output_dir,
        title=title,
        author=author,
        notes=notes,
        dpi=dpi,
        bbox_inches=bbox_inches
    ) 