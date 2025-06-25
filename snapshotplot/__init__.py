"""
SnapshotPlot - Capture Python code, Matplotlib plots, and HTML documentation in one step.

This package provides a simple way to automatically capture and document your plotting code
with unified timestamping and beautiful HTML output.
"""

from .snapshot import snapshot, SnapshotContext

__version__ = "0.1.0"
__author__ = "SnapshotPlot Team"
__email__ = "team@snapshotplot.dev"

__all__ = ["snapshot", "SnapshotContext"] 