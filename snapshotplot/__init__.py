"""
SnapshotPlot - Capture Python code, Matplotlib plots, and HTML documentation in one step.

This package provides a simple way to automatically capture and document your plotting code
with unified timestamping and beautiful HTML output.
"""

from .core import snapshot, SnapshotContext, get_timestamp

__version__ = "0.1.0"
__author__ = "SnapshotPlot Team"
__email__ = "team@snapshotplot.dev"

__all__ = ["snapshot", "SnapshotContext", "get_timestamp"]

# Optional Jupyter integration
try:
    from .jupyter import (
        SnapshotMagics,
        notebook_snapshot, 
        load_ipython_extension,
        is_notebook,
        get_notebook_info,
        unload_ipython_extension
    )
    __all__.extend(['SnapshotMagics', 'notebook_snapshot', 'load_ipython_extension', 'is_notebook', 'get_notebook_info', 'unload_ipython_extension'])
except ImportError:
    # Jupyter/IPython not available
    pass 