"""
Core snapshot functionality for snapshotplot.

This module provides the main decorator and context manager for capturing
Python code, matplotlib plots, and generating HTML documentation.
"""

import functools
import os
from typing import Optional, Callable, Any, Dict, Union
from contextlib import contextmanager
from pathlib import Path

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
from .visualization_backends import BackendRegistry
from .export_formats import ExportFormatRegistry


class SnapshotContext:
    """Context manager for snapshot functionality."""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        notes: Optional[str] = None,
        dpi: int = 300,
        bbox_inches: str = 'tight',
        # Site generator options
        site: Optional[str] = None,
        collection: Optional[str] = None,
        tags: Optional[list] = None,
        description: Optional[str] = None,
        auto_commit: bool = False,
        auto_build: bool = False,
        auto_deploy: bool = False,
        # New enhancement parameters
        backend: Optional[str] = None,
        export_formats: Optional[list] = None,
        enable_search: bool = False
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
            site: Site directory for static site generation
            collection: Collection name for organizing plots
            tags: List of tags for categorizing plots
            description: Description for the plot
            auto_commit: Automatically commit to git after snapshot
            auto_build: Automatically build static site after snapshot
            auto_deploy: Automatically deploy site after snapshot
            backend: Visualization backend to use ('matplotlib', 'plotly', 'altair')
            export_formats: List of export formats ('html', 'pdf', 'markdown', 'latex', 'jupyter')
            enable_search: Enable search indexing for this snapshot
        """
        self.config = {
            'output_dir': output_dir,
            'title': title,
            'author': author,
            'notes': notes,
            'dpi': dpi,
            'bbox_inches': bbox_inches,
            'site': site,
            'collection': collection,
            'tags': tags or [],
            'description': description,
            'auto_commit': auto_commit,
            'auto_build': auto_build,
            'auto_deploy': auto_deploy,
            'backend': backend,
            'export_formats': export_formats or ['html'],
            'enable_search': enable_search
        }
        
        # Validate and merge with defaults
        default_config = get_default_config()
        self.config = merge_configs(default_config, validate_config(self.config))
        
        # Initialize state
        self.timestamp = None
        self.calling_info = None
        self.file_paths = None
        
        # Initialize backend registry
        self.backend_registry = BackendRegistry()
        
        # Initialize export format registry
        self.export_registry = ExportFormatRegistry()
        
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
        plot_data = self._save_plot()
        
        # Create documentation in all requested formats
        self._create_documentation(plot_data)
        
        # Handle site generation if configured
        if self.config.get('site') or self.config.get('collection'):
            self._handle_site_generation()
        
        # Handle git operations
        if self.config.get('auto_commit'):
            self._auto_commit()
        
        # Handle site building/deployment
        if self.config.get('auto_build'):
            self._auto_build()
        
        if self.config.get('auto_deploy'):
            self._auto_deploy()
    
    def _save_source_code(self):
        """Save the source code to a file."""
        try:
            with open(self.file_paths['code'], 'w', encoding='utf-8') as f:
                f.write(self.calling_info['source_code'])
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to save source code: {e}")
    
    def _save_plot(self) -> dict:
        """Save plots using the configured visualization backend."""
        try:
            # Get the backend (default to matplotlib for backward compatibility)
            backend_name = self.config.get('backend', 'matplotlib')
            backend = self.backend_registry.get_backend(backend_name)
            
            if not backend.detect_active_plots():
                return {'saved': False, 'files': []}
            
            # Save plots in the configured formats
            plot_files = backend.save_plots(
                output_dir=os.path.dirname(self.file_paths['plot']),
                timestamp=self.timestamp,
                formats=['png']  # Default format for backward compatibility
            )
            
            return {'saved': True, 'files': plot_files}
            
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to save plot: {e}")
            return {'saved': False, 'files': []}
    
    def _create_documentation(self, plot_data: dict):
        """Create documentation in all requested formats."""
        try:
            from .export_formats import ExportContext
            
            # Prepare metadata
            metadata = {
                'function_name': self.calling_info['function_name'],
                'filename': self.calling_info['filename'],
                'date': format_timestamp_for_display(self.timestamp)
            }
            
            # Prepare export context
            plot_files = plot_data.get('files', [])
            plot_paths = [Path(pf['path']) for pf in plot_files] if plot_files else []
            
            context = ExportContext(
                code=self.calling_info['source_code'],
                plot_paths=plot_paths,
                metadata=metadata,
                timestamp=self.timestamp,
                output_dir=Path(os.path.dirname(self.file_paths['html'])),
                title=self.config['title'],
                author=self.config['author'],
                notes=self.config['notes']
            )
            
            # Export in all requested formats
            for format_name in self.config['export_formats']:
                try:
                    exporter = self.export_registry.get_format(format_name)
                    exporter.export(context)
                except Exception as e:
                    import warnings
                    warnings.warn(f"Failed to export {format_name}: {e}")
                    
            # Handle search indexing if enabled
            if self.config.get('enable_search'):
                self._index_snapshot(context)
                
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to create documentation: {e}")
    
    def _index_snapshot(self, context):
        """Index the snapshot for search functionality."""
        try:
            from .search_system import SnapshotSearchManager, SnapshotIndex
            from datetime import datetime
            
            # Create search manager
            output_dir = Path(self.config.get('output_dir', 'snapshots'))
            search_manager = SnapshotSearchManager(output_dir)
            
            # Create snapshot index object with our programmatic data
            snapshot_index = SnapshotIndex(
                id=self.timestamp,
                timestamp=datetime.now().isoformat(),
                title=context.title or self.calling_info['function_name'],
                author=context.author,
                filename=self.calling_info['filename'],
                function_name=self.calling_info['function_name'],
                description=context.notes or '',
                tags=self.config.get('tags', []),
                code_content=context.code,
                plot_paths=[str(p) for p in context.plot_paths],
                file_size_bytes=len(context.code.encode('utf-8')),
                creation_date=datetime.now(),
                last_modified=datetime.now(),
                metadata={
                    'backend': self.config.get('backend', 'matplotlib'),
                    'export_formats': self.config.get('export_formats', ['html']),
                    'code_length': len(context.code),
                    'plot_count': len(context.plot_paths)
                }
            )
            
            # Add directly to search index
            search_manager.index.add_snapshot(snapshot_index)
            
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to index snapshot: {e}")
    
    def _handle_site_generation(self):
        """Handle site generation integration."""
        try:
            import os
            import yaml
            from datetime import datetime
            from pathlib import Path
            
            # Determine site directory
            site_dir = self.config.get('site', '.')
            collection = self.config.get('collection', 'plots')
            
            site_path = Path(site_dir)
            config_path = site_path / '_config.yml'
            
            # Check if this is a site directory
            if not config_path.exists():
                import warnings
                warnings.warn(f"Site directory {site_dir} doesn't contain _config.yml. Skipping site generation.")
                return
            
            # Create collection directory structure
            collection_dir = site_path / 'collections' / collection
            collection_dir.mkdir(parents=True, exist_ok=True)
            
            # Create plot directory with timestamp
            plot_dir = collection_dir / f"{self.timestamp}_{sanitize_filename(self.config.get('title', 'plot'))}"
            plot_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files to site structure
            import shutil
            
            # Copy plot files
            plot_files = plot_data.get('files', [])
            if plot_files:
                # Use the first plot file for backward compatibility
                plot_file = plot_files[0]
                shutil.copy2(plot_file['path'], plot_dir / 'plot.png')
            
            # Copy source code
            if os.path.exists(self.file_paths['code']):
                shutil.copy2(self.file_paths['code'], plot_dir / 'code.py')
            
            # Create plot metadata file
            metadata = {
                'title': self.config.get('title') or self.calling_info['function_name'],
                'date': datetime.now().isoformat(),
                'author': self.config.get('author'),
                'description': self.config.get('description'),
                'tags': self.config.get('tags', []),
                'plot_image': 'plot.png',
                'code_file': 'code.py',
                'function_name': self.calling_info['function_name'],
                'filename': self.calling_info['filename']
            }
            
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            with open(plot_dir / 'index.md', 'w') as f:
                f.write('---\n')
                yaml.dump(metadata, f, default_flow_style=False)
                f.write('---\n\n')
                if self.config.get('description'):
                    f.write(f"{self.config['description']}\n\n")
                f.write(f"Generated from `{self.calling_info['function_name']}` in `{self.calling_info['filename']}`\n")
            
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to handle site generation: {e}")
    
    def _auto_commit(self):
        """Automatically commit changes to git."""
        try:
            import subprocess
            subprocess.run(['git', 'add', '.'], cwd=self.config.get('site', '.'), check=True)
            commit_msg = f"Add plot: {self.config.get('title', 'Unnamed plot')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=self.config.get('site', '.'), check=True)
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to auto-commit: {e}")
    
    def _auto_build(self):
        """Automatically build the static site."""
        try:
            from .site_generator import SiteGenerator
            site_dir = self.config.get('site', '.')
            generator = SiteGenerator(site_dir)
            generator.build()
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to auto-build site: {e}")
    
    def _auto_deploy(self):
        """Automatically deploy the site."""
        try:
            import subprocess
            site_dir = self.config.get('site', '.')
            subprocess.run(['git', 'add', 'docs/'], cwd=site_dir, check=True)
            subprocess.run(['git', 'commit', '-m', 'Deploy site'], cwd=site_dir, check=True)
            subprocess.run(['git', 'push'], cwd=site_dir, check=True)
        except Exception as e:
            import warnings
            warnings.warn(f"Failed to auto-deploy: {e}")


class SnapshotDecorator:
    """Decorator class that can also be used as a context manager."""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        notes: Optional[str] = None,
        dpi: int = 300,
        bbox_inches: str = 'tight',
        # Site generator options
        site: Optional[str] = None,
        collection: Optional[str] = None,
        tags: Optional[list] = None,
        description: Optional[str] = None,
        auto_commit: bool = False,
        auto_build: bool = False,
        auto_deploy: bool = False,
        # New enhancement parameters
        backend: Optional[str] = None,
        export_formats: Optional[list] = None,
        enable_search: bool = False
    ):
        """Initialize the decorator with configuration."""
        self.config = {
            'output_dir': output_dir,
            'title': title,
            'author': author,
            'notes': notes,
            'dpi': dpi,
            'bbox_inches': bbox_inches,
            'site': site,
            'collection': collection,
            'tags': tags or [],
            'description': description,
            'auto_commit': auto_commit,
            'auto_build': auto_build,
            'auto_deploy': auto_deploy,
            'backend': backend,
            'export_formats': export_formats or ['html'],
            'enable_search': enable_search
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
    bbox_inches: str = 'tight',
    # Site generator options
    site: Optional[str] = None,
    collection: Optional[str] = None,
    tags: Optional[list] = None,
    description: Optional[str] = None,
    auto_commit: bool = False,
    auto_build: bool = False,
    auto_deploy: bool = False,
    # New enhancement parameters
    backend: Optional[str] = None,
    export_formats: Optional[list] = None,
    enable_search: bool = False
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
        bbox_inches=bbox_inches,
        site=site,
        collection=collection,
        tags=tags,
        description=description,
        auto_commit=auto_commit,
        auto_build=auto_build,
        auto_deploy=auto_deploy,
        backend=backend,
        export_formats=export_formats,
        enable_search=enable_search
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