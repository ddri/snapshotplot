"""Core SnapshotPlot functionality for capturing code and plots."""

from .snapshot import snapshot, SnapshotContext
from .timestamp import get_timestamp
__all__ = ['snapshot', 'SnapshotContext', 'get_timestamp']