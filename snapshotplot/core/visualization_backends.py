"""
Multi-library visualization backend system for SnapshotPlot.

This module provides a plugin architecture for supporting multiple visualization
libraries beyond matplotlib, enabling users to work with their preferred tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import inspect
import warnings
from dataclasses import dataclass


@dataclass
class PlotMetadata:
    """Metadata about a captured plot."""
    library: str
    plot_type: str
    dimensions: Optional[Tuple[int, int]] = None
    interactive: bool = False
    file_size_bytes: Optional[int] = None
    additional_info: Dict[str, Any] = None


class VisualizationBackend(ABC):
    """Abstract base class for visualization backends."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Backend name (e.g., 'matplotlib', 'plotly')."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """List of supported export formats."""
        pass
    
    @abstractmethod
    def detect_active_plots(self) -> bool:
        """Check if this backend has active plots to capture."""
        pass
    
    @abstractmethod
    def save_plots(self, output_dir: Path, timestamp: str, 
                   formats: List[str] = None) -> List[Dict[str, Any]]:
        """
        Save all active plots from this backend.
        
        Returns:
            List of saved plot info: [{'path': Path, 'format': str, 'metadata': PlotMetadata}]
        """
        pass
    
    @abstractmethod
    def get_plot_metadata(self) -> List[PlotMetadata]:
        """Get metadata about active plots."""
        pass
    
    def cleanup(self):
        """Clean up any backend-specific resources."""
        pass


class MatplotlibBackend(VisualizationBackend):
    """Backend for matplotlib plots."""
    
    @property
    def name(self) -> str:
        return "matplotlib"
    
    @property
    def supported_formats(self) -> List[str]:
        return ["png", "svg", "pdf", "eps", "jpg"]
    
    def detect_active_plots(self) -> bool:
        """Check for active matplotlib figures."""
        try:
            import matplotlib.pyplot as plt
            fig = plt.gcf()
            return len(fig.axes) > 0
        except Exception:
            return False
    
    def save_plots(self, output_dir: Path, timestamp: str, 
                   formats: List[str] = None) -> List[Dict[str, Any]]:
        """Save matplotlib figures."""
        if formats is None:
            formats = ["png"]
        
        try:
            import matplotlib.pyplot as plt
            fig = plt.gcf()
            
            if len(fig.axes) == 0:
                return []
            
            saved_plots = []
            for fmt in formats:
                plot_path = Path(output_dir) / f"{timestamp}_plot.{fmt}"
                
                fig.savefig(
                    plot_path,
                    dpi=300,
                    format=fmt,
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                
                # Get plot metadata
                metadata = PlotMetadata(
                    library="matplotlib",
                    plot_type="figure",
                    dimensions=(fig.get_figwidth(), fig.get_figheight()),
                    interactive=False,
                    file_size_bytes=plot_path.stat().st_size if plot_path.exists() else None
                )
                
                saved_plots.append({
                    'path': plot_path,
                    'format': fmt,
                    'metadata': metadata
                })
            
            return saved_plots
            
        except Exception as e:
            warnings.warn(f"Failed to save matplotlib plot: {e}")
            return []
    
    def get_plot_metadata(self) -> List[PlotMetadata]:
        """Get metadata about active matplotlib figures."""
        try:
            import matplotlib.pyplot as plt
            fig = plt.gcf()
            
            if len(fig.axes) == 0:
                return []
            
            return [PlotMetadata(
                library="matplotlib",
                plot_type="figure",
                dimensions=(fig.get_figwidth(), fig.get_figheight()),
                interactive=False,
                additional_info={
                    'num_axes': len(fig.axes),
                    'title': fig._suptitle.get_text() if fig._suptitle else None
                }
            )]
        except Exception:
            return []


class PlotlyBackend(VisualizationBackend):
    """Backend for Plotly plots."""
    
    @property
    def name(self) -> str:
        return "plotly"
    
    @property
    def supported_formats(self) -> List[str]:
        return ["html", "png", "svg", "pdf", "json"]
    
    def detect_active_plots(self) -> bool:
        """Check for active Plotly figures in the current execution context."""
        try:
            import plotly.graph_objects as go
            
            # Get the calling frame to check for plotly figures
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_locals = frame.f_back.f_locals
                caller_globals = frame.f_back.f_globals
                
                # Check locals and globals for plotly figures
                for var_dict in [caller_locals, caller_globals]:
                    for var_name, var_value in var_dict.items():
                        if isinstance(var_value, go.Figure):
                            return True
                        # Check for list/dict containing figures
                        elif isinstance(var_value, (list, tuple)):
                            if any(isinstance(item, go.Figure) for item in var_value):
                                return True
                        elif isinstance(var_value, dict):
                            if any(isinstance(item, go.Figure) for item in var_value.values()):
                                return True
            
            return False
        except ImportError:
            return False
        except Exception:
            return False
    
    def save_plots(self, output_dir: Path, timestamp: str, 
                   formats: List[str] = None) -> List[Dict[str, Any]]:
        """Save Plotly figures."""
        if formats is None:
            formats = ["html", "png"]
        
        try:
            import plotly.graph_objects as go
            
            figures = self._find_plotly_figures()
            if not figures:
                return []
            
            saved_plots = []
            
            for i, fig in enumerate(figures):
                suffix = f"_{i}" if len(figures) > 1 else ""
                
                for fmt in formats:
                    if fmt == "html":
                        plot_path = output_dir / f"{timestamp}_plot{suffix}.html"
                        fig.write_html(
                            plot_path,
                            include_plotlyjs='inline',
                            config={'displayModeBar': True}
                        )
                    elif fmt == "json":
                        plot_path = output_dir / f"{timestamp}_plot{suffix}.json"
                        fig.write_json(plot_path)
                    else:
                        # Static formats (png, svg, pdf)
                        plot_path = output_dir / f"{timestamp}_plot{suffix}.{fmt}"
                        fig.write_image(
                            plot_path,
                            format=fmt,
                            width=800,
                            height=600,
                            scale=2  # High DPI
                        )
                    
                    # Get plot metadata
                    metadata = PlotMetadata(
                        library="plotly",
                        plot_type=self._get_plotly_chart_type(fig),
                        dimensions=(800, 600),  # Default Plotly dimensions
                        interactive=(fmt in ["html", "json"]),
                        file_size_bytes=plot_path.stat().st_size if plot_path.exists() else None,
                        additional_info={
                            'trace_count': len(fig.data),
                            'layout_title': fig.layout.title.text if fig.layout.title else None
                        }
                    )
                    
                    saved_plots.append({
                        'path': plot_path,
                        'format': fmt,
                        'metadata': metadata
                    })
            
            return saved_plots
            
        except ImportError:
            warnings.warn("Plotly not available for plot capture")
            return []
        except Exception as e:
            warnings.warn(f"Failed to save Plotly plot: {e}")
            return []
    
    def _find_plotly_figures(self) -> List[Any]:
        """Find Plotly figures in the execution context."""
        try:
            import plotly.graph_objects as go
            
            figures = []
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_locals = frame.f_back.f_locals
                caller_globals = frame.f_back.f_globals
                
                for var_dict in [caller_locals, caller_globals]:
                    for var_name, var_value in var_dict.items():
                        if isinstance(var_value, go.Figure):
                            figures.append(var_value)
                        elif isinstance(var_value, (list, tuple)):
                            figures.extend([item for item in var_value 
                                          if isinstance(item, go.Figure)])
                        elif isinstance(var_value, dict):
                            figures.extend([item for item in var_value.values() 
                                          if isinstance(item, go.Figure)])
            
            return figures
        except Exception:
            return []
    
    def _get_plotly_chart_type(self, fig) -> str:
        """Determine the primary chart type of a Plotly figure."""
        if not fig.data:
            return "empty"
        
        # Get the most common trace type
        trace_types = [trace.type for trace in fig.data if hasattr(trace, 'type')]
        if trace_types:
            return max(set(trace_types), key=trace_types.count)
        
        return "unknown"
    
    def get_plot_metadata(self) -> List[PlotMetadata]:
        """Get metadata about active Plotly figures."""
        figures = self._find_plotly_figures()
        metadata_list = []
        
        for fig in figures:
            metadata = PlotMetadata(
                library="plotly",
                plot_type=self._get_plotly_chart_type(fig),
                interactive=True,
                additional_info={
                    'trace_count': len(fig.data),
                    'has_annotations': len(fig.layout.annotations) > 0 if fig.layout.annotations else False,
                    'has_shapes': len(fig.layout.shapes) > 0 if fig.layout.shapes else False
                }
            )
            metadata_list.append(metadata)
        
        return metadata_list


class AltairBackend(VisualizationBackend):
    """Backend for Altair/Vega-Lite plots."""
    
    @property
    def name(self) -> str:
        return "altair"
    
    @property
    def supported_formats(self) -> List[str]:
        return ["html", "png", "svg", "pdf", "json"]
    
    def detect_active_plots(self) -> bool:
        """Check for active Altair charts."""
        try:
            import altair as alt
            
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_locals = frame.f_back.f_locals
                caller_globals = frame.f_back.f_globals
                
                for var_dict in [caller_locals, caller_globals]:
                    for var_value in var_dict.values():
                        if isinstance(var_value, alt.Chart):
                            return True
                        elif isinstance(var_value, (list, tuple)):
                            if any(isinstance(item, alt.Chart) for item in var_value):
                                return True
            
            return False
        except ImportError:
            return False
        except Exception:
            return False
    
    def save_plots(self, output_dir: Path, timestamp: str, 
                   formats: List[str] = None) -> List[Dict[str, Any]]:
        """Save Altair charts."""
        if formats is None:
            formats = ["html", "png"]
        
        try:
            import altair as alt
            
            charts = self._find_altair_charts()
            if not charts:
                return []
            
            saved_plots = []
            
            for i, chart in enumerate(charts):
                suffix = f"_{i}" if len(charts) > 1 else ""
                
                for fmt in formats:
                    plot_path = output_dir / f"{timestamp}_plot{suffix}.{fmt}"
                    
                    if fmt == "json":
                        # Save Vega-Lite specification
                        chart.save(str(plot_path))
                    elif fmt == "html":
                        # Save as standalone HTML
                        chart.save(str(plot_path))
                    else:
                        # Static formats
                        chart.save(str(plot_path), format=fmt, ppi=300)
                    
                    # Get plot metadata
                    metadata = PlotMetadata(
                        library="altair",
                        plot_type=self._get_altair_chart_type(chart),
                        interactive=(fmt in ["html", "json"]),
                        file_size_bytes=plot_path.stat().st_size if plot_path.exists() else None,
                        additional_info={
                            'encoding_channels': self._get_encoding_info(chart),
                            'data_rows': self._get_data_size(chart)
                        }
                    )
                    
                    saved_plots.append({
                        'path': plot_path,
                        'format': fmt,
                        'metadata': metadata
                    })
            
            return saved_plots
            
        except ImportError:
            warnings.warn("Altair not available for plot capture")
            return []
        except Exception as e:
            warnings.warn(f"Failed to save Altair chart: {e}")
            return []
    
    def _find_altair_charts(self) -> List[Any]:
        """Find Altair charts in the execution context."""
        try:
            import altair as alt
            
            charts = []
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_locals = frame.f_back.f_locals
                caller_globals = frame.f_back.f_globals
                
                for var_dict in [caller_locals, caller_globals]:
                    for var_value in var_dict.values():
                        if isinstance(var_value, alt.Chart):
                            charts.append(var_value)
                        elif isinstance(var_value, (list, tuple)):
                            charts.extend([item for item in var_value 
                                         if isinstance(item, alt.Chart)])
            
            return charts
        except Exception:
            return []
    
    def _get_altair_chart_type(self, chart) -> str:
        """Determine Altair chart type from mark."""
        try:
            mark = chart.mark
            if hasattr(mark, 'type'):
                return mark.type
            elif hasattr(mark, '__class__'):
                return mark.__class__.__name__.lower().replace('mark', '')
            return "unknown"
        except Exception:
            return "unknown"
    
    def _get_encoding_info(self, chart) -> Dict[str, Any]:
        """Get encoding channel information."""
        try:
            encoding = chart.encoding
            channels = {}
            for channel_name in ['x', 'y', 'color', 'size', 'shape']:
                if hasattr(encoding, channel_name):
                    channel = getattr(encoding, channel_name)
                    if channel:
                        channels[channel_name] = {
                            'field': getattr(channel, 'field', None),
                            'type': getattr(channel, 'type', None)
                        }
            return channels
        except Exception:
            return {}
    
    def _get_data_size(self, chart) -> Optional[int]:
        """Get number of data rows if possible."""
        try:
            if hasattr(chart, 'data') and chart.data is not None:
                import pandas as pd
                if isinstance(chart.data, pd.DataFrame):
                    return len(chart.data)
                elif isinstance(chart.data, dict) and 'values' in chart.data:
                    return len(chart.data['values'])
            return None
        except Exception:
            return None
    
    def get_plot_metadata(self) -> List[PlotMetadata]:
        """Get metadata about active Altair charts."""
        charts = self._find_altair_charts()
        metadata_list = []
        
        for chart in charts:
            metadata = PlotMetadata(
                library="altair",
                plot_type=self._get_altair_chart_type(chart),
                interactive=True,
                additional_info={
                    'encoding_channels': self._get_encoding_info(chart),
                    'data_rows': self._get_data_size(chart)
                }
            )
            metadata_list.append(metadata)
        
        return metadata_list


class BackendRegistry:
    """Registry for managing visualization backends."""
    
    def __init__(self):
        self.backends: Dict[str, VisualizationBackend] = {}
        self._register_default_backends()
    
    def _register_default_backends(self):
        """Register built-in backends."""
        self.register_backend(MatplotlibBackend())
        
        # Register optional backends if libraries are available
        try:
            import plotly
            self.register_backend(PlotlyBackend())
        except ImportError:
            pass
        
        try:
            import altair
            self.register_backend(AltairBackend())
        except ImportError:
            pass
    
    def register_backend(self, backend: VisualizationBackend):
        """Register a visualization backend."""
        self.backends[backend.name] = backend
    
    def get_backend(self, name: str) -> Optional[VisualizationBackend]:
        """Get a backend by name."""
        return self.backends.get(name)
    
    def detect_active_backends(self) -> List[str]:
        """Detect which backends have active plots."""
        active_backends = []
        for name, backend in self.backends.items():
            try:
                if backend.detect_active_plots():
                    active_backends.append(name)
            except Exception as e:
                warnings.warn(f"Error detecting plots in {name} backend: {e}")
        
        return active_backends
    
    def save_all_plots(self, output_dir: Path, timestamp: str, 
                       formats: Dict[str, List[str]] = None,
                       priority_order: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Save plots from all active backends.
        
        Args:
            output_dir: Directory to save plots
            timestamp: Timestamp for file naming
            formats: Dict mapping backend names to format lists
            priority_order: Order to process backends (first wins for conflicts)
        
        Returns:
            Dict mapping backend names to saved plot info
        """
        if formats is None:
            formats = {}
        
        if priority_order is None:
            priority_order = ["plotly", "altair", "matplotlib"]  # Interactive first
        
        active_backends = self.detect_active_backends()
        results = {}
        
        # Process backends in priority order
        for backend_name in priority_order:
            if backend_name in active_backends:
                backend = self.backends[backend_name]
                backend_formats = formats.get(backend_name, ["png", "html"])
                
                try:
                    saved_plots = backend.save_plots(output_dir, timestamp, backend_formats)
                    if saved_plots:
                        results[backend_name] = saved_plots
                        # For most use cases, capture from first active backend only
                        break
                except Exception as e:
                    warnings.warn(f"Failed to save plots from {backend_name}: {e}")
        
        return results
    
    def get_all_metadata(self) -> Dict[str, List[PlotMetadata]]:
        """Get metadata from all backends with active plots."""
        all_metadata = {}
        
        for name, backend in self.backends.items():
            try:
                if backend.detect_active_plots():
                    metadata = backend.get_plot_metadata()
                    if metadata:
                        all_metadata[name] = metadata
            except Exception as e:
                warnings.warn(f"Error getting metadata from {name}: {e}")
        
        return all_metadata
    
    def cleanup_all(self):
        """Clean up resources from all backends."""
        for backend in self.backends.values():
            try:
                backend.cleanup()
            except Exception as e:
                warnings.warn(f"Error cleaning up {backend.name}: {e}")


# Global registry instance
_global_registry = BackendRegistry()


def get_visualization_registry() -> BackendRegistry:
    """Get the global visualization backend registry."""
    return _global_registry


def register_custom_backend(backend: VisualizationBackend):
    """Register a custom visualization backend."""
    _global_registry.register_backend(backend)


def detect_active_visualizations() -> Dict[str, List[PlotMetadata]]:
    """Detect all active visualizations across all backends."""
    return _global_registry.get_all_metadata()


def save_detected_plots(output_dir: Path, timestamp: str, 
                       formats: Dict[str, List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Save plots from all detected visualization libraries."""
    return _global_registry.save_all_plots(output_dir, timestamp, formats)