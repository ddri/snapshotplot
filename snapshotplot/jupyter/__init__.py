"""Jupyter notebook integration for SnapshotPlot."""

try:
    # Only import if IPython is available
    from IPython.core.magic import Magics
    from .jupyter_integration import (
        SnapshotMagics, 
        notebook_snapshot, 
        is_notebook,
        get_notebook_info,
        load_ipython_extension,
        unload_ipython_extension
    )
    __all__ = [
        'SnapshotMagics', 
        'notebook_snapshot', 
        'is_notebook', 
        'get_notebook_info',
        'load_ipython_extension',
        'unload_ipython_extension'
    ]
except ImportError:
    # IPython not available - create stub functions
    def is_notebook():
        return False
    
    def get_notebook_info():
        return {}
    
    def notebook_snapshot(*args, **kwargs):
        from ..core import snapshot
        return snapshot(*args, **kwargs)
    
    __all__ = ['is_notebook', 'get_notebook_info', 'notebook_snapshot']