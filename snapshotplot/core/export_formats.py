"""
Export format system for SnapshotPlot.

This module provides a extensible system for exporting snapshots to various
formats beyond the default HTML, enabling integration with different workflows.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
import tempfile
import warnings


@dataclass
class ExportContext:
    """Context information for export operations."""
    code: str
    plot_paths: List[Path]
    metadata: Dict[str, Any]
    timestamp: str
    output_dir: Path
    title: Optional[str] = None
    author: Optional[str] = None
    notes: Optional[str] = None


class ExportFormat(ABC):
    """Abstract base class for export formats."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Format name (e.g., 'pdf', 'markdown')."""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for this format."""
        pass
    
    @property
    @abstractmethod
    def mime_type(self) -> str:
        """MIME type for this format."""
        pass
    
    @abstractmethod
    def export(self, context: ExportContext) -> Path:
        """
        Export snapshot to this format.
        
        Args:
            context: Export context with code, plots, and metadata
            
        Returns:
            Path to the exported file
        """
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """List of required dependencies for this format."""
        return []
    
    def is_available(self) -> bool:
        """Check if all dependencies are available."""
        for dep in self.dependencies:
            try:
                __import__(dep)
            except ImportError:
                return False
        return True


class HTMLExportFormat(ExportFormat):
    """HTML export format (existing functionality)."""
    
    @property
    def name(self) -> str:
        return "html"
    
    @property
    def file_extension(self) -> str:
        return "html"
    
    @property
    def mime_type(self) -> str:
        return "text/html"
    
    def export(self, context: ExportContext) -> Path:
        """Export to HTML using existing template system."""
        from .html_writer import create_html_snapshot
        
        html_path = context.output_dir / f"{context.timestamp}_snapshot.html"
        
        # Use existing HTML generation
        plot_path = context.plot_paths[0] if context.plot_paths else None
        create_html_snapshot(
            code=context.code,
            plot_path=str(plot_path) if plot_path else '',
            html_path=str(html_path),
            metadata=context.metadata,
            title=context.title,
            author=context.author,
            notes=context.notes
        )
        
        return html_path


class PDFExportFormat(ExportFormat):
    """PDF export format using WeasyPrint."""
    
    @property
    def name(self) -> str:
        return "pdf"
    
    @property
    def file_extension(self) -> str:
        return "pdf"
    
    @property
    def mime_type(self) -> str:
        return "application/pdf"
    
    @property
    def dependencies(self) -> List[str]:
        return ["weasyprint"]
    
    def export(self, context: ExportContext) -> Path:
        """Export to PDF via HTML intermediate."""
        try:
            import weasyprint
            from .html_writer import create_html_snapshot
            
            # Generate HTML first
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                temp_html_path = Path(f.name)
            
            plot_path = context.plot_paths[0] if context.plot_paths else None
            create_html_snapshot(
                code=context.code,
                plot_path=str(plot_path) if plot_path else '',
                html_path=str(temp_html_path),
                metadata=context.metadata,
                title=context.title,
                author=context.author,
                notes=context.notes
            )
            
            # Convert HTML to PDF
            pdf_path = context.output_dir / f"{context.timestamp}_snapshot.pdf"
            
            html_doc = weasyprint.HTML(filename=str(temp_html_path))
            html_doc.write_pdf(str(pdf_path))
            
            # Cleanup
            temp_html_path.unlink()
            
            return pdf_path
            
        except ImportError:
            raise RuntimeError("WeasyPrint not available. Install with: pip install weasyprint")
        except Exception as e:
            raise RuntimeError(f"PDF export failed: {e}")


class MarkdownExportFormat(ExportFormat):
    """Markdown export format with YAML front matter."""
    
    @property
    def name(self) -> str:
        return "markdown"
    
    @property
    def file_extension(self) -> str:
        return "md"
    
    @property
    def mime_type(self) -> str:
        return "text/markdown"
    
    @property
    def dependencies(self) -> List[str]:
        return ["yaml"]
    
    def export(self, context: ExportContext) -> Path:
        """Export to Markdown with YAML front matter."""
        import yaml
        
        md_path = context.output_dir / f"{context.timestamp}_snapshot.md"
        
        # Prepare front matter
        front_matter = {
            'title': context.metadata.get('function_name', 'Code Snapshot'),
            'date': context.metadata.get('date'),
            'author': context.metadata.get('author') or context.author,
            'tags': context.metadata.get('tags', []),
            'filename': context.metadata.get('filename'),
            'timestamp': context.timestamp
        }
        
        # Clean up None values
        front_matter = {k: v for k, v in front_matter.items() if v is not None}
        
        # Build markdown content
        content_parts = [
            "---",
            yaml.dump(front_matter, default_flow_style=False).strip(),
            "---",
            "",
            f"# {front_matter.get('title', 'Code Snapshot')}",
            ""
        ]
        
        # Add metadata section if available
        if context.metadata.get('description'):
            content_parts.extend([
                context.metadata['description'],
                ""
            ])
        
        # Add source code section
        content_parts.extend([
            "## Source Code",
            "",
            "```python",
            context.code.strip(),
            "```",
            ""
        ])
        
        # Add plot section if plots exist
        if context.plot_paths:
            content_parts.extend(["## Generated Plots", ""])
            
            for i, plot_path in enumerate(context.plot_paths):
                plot_name = plot_path.name
                content_parts.extend([
                    f"![Plot {i+1}]({plot_name})",
                    ""
                ])
        
        # Add execution details
        if context.metadata.get('execution_time'):
            content_parts.extend([
                "## Execution Details",
                "",
                f"- **Execution Time**: {context.metadata['execution_time']}",
                f"- **Generated**: {front_matter.get('date', 'Unknown')}",
                ""
            ])
        
        # Write markdown file
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_parts))
        
        return md_path


class JupyterNotebookExportFormat(ExportFormat):
    """Jupyter notebook export format."""
    
    @property
    def name(self) -> str:
        return "notebook"
    
    @property
    def file_extension(self) -> str:
        return "ipynb"
    
    @property
    def mime_type(self) -> str:
        return "application/x-ipynb+json"
    
    @property
    def dependencies(self) -> List[str]:
        return ["nbformat"]
    
    def export(self, context: ExportContext) -> Path:
        """Export to Jupyter notebook format."""
        try:
            import nbformat as nbf
            import base64
            
            # Create new notebook
            nb = nbf.v4.new_notebook()
            nb.metadata = {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.9"
                },
                "snapshotplot": {
                    "timestamp": context.timestamp,
                    "original_file": context.metadata.get('filename'),
                    "author": context.metadata.get('author')
                }
            }
            
            # Add markdown cell with metadata
            title = context.metadata.get('function_name', 'Code Snapshot')
            markdown_content = f"""# {title}
            
**Generated**: {context.metadata.get('date', 'Unknown')}  
**Author**: {context.metadata.get('author', 'Unknown')}  
**Source**: {context.metadata.get('filename', 'Unknown')}

{context.metadata.get('description', '')}
"""
            
            nb.cells.append(nbf.v4.new_markdown_cell(markdown_content.strip()))
            
            # Add code cell with execution
            code_cell = nbf.v4.new_code_cell(context.code)
            
            # Add plot outputs if available
            if context.plot_paths:
                outputs = []
                
                for plot_path in context.plot_paths:
                    if plot_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                        # Add image output
                        with open(plot_path, 'rb') as f:
                            plot_data = base64.b64encode(f.read()).decode('utf-8')
                        
                        output = nbf.v4.new_output(
                            output_type='display_data',
                            data={
                                'image/png': plot_data
                            },
                            metadata={
                                'image/png': {
                                    'width': 800,
                                    'height': 600
                                }
                            }
                        )
                        outputs.append(output)
                    
                    elif plot_path.suffix.lower() == '.html':
                        # Add HTML output for interactive plots
                        with open(plot_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        output = nbf.v4.new_output(
                            output_type='display_data',
                            data={
                                'text/html': html_content
                            }
                        )
                        outputs.append(output)
                
                code_cell.outputs = outputs
            
            nb.cells.append(code_cell)
            
            # Save notebook
            notebook_path = context.output_dir / f"{context.timestamp}_snapshot.ipynb"
            with open(notebook_path, 'w', encoding='utf-8') as f:
                nbf.write(nb, f)
            
            return notebook_path
            
        except ImportError:
            raise RuntimeError("nbformat not available. Install with: pip install nbformat")
        except Exception as e:
            raise RuntimeError(f"Notebook export failed: {e}")


class LaTeXExportFormat(ExportFormat):
    """LaTeX export format for academic publishing."""
    
    @property
    def name(self) -> str:
        return "latex"
    
    @property
    def file_extension(self) -> str:
        return "tex"
    
    @property
    def mime_type(self) -> str:
        return "application/x-latex"
    
    def export(self, context: ExportContext) -> Path:
        """Export to LaTeX format."""
        from jinja2 import Template
        
        latex_template = r"""
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{listings}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{geometry}
\usepackage{fancyhdr}

\geometry{margin=1in}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{ {{- title -}} }
\fancyhead[R]{ {{- date -}} }
\fancyfoot[C]{\thepage}

% Python syntax highlighting
\lstset{
    language=Python,
    backgroundcolor=\color{gray!10},
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue},
    commentstyle=\color{green!60!black},
    stringstyle=\color{red},
    numbers=left,
    numberstyle=\tiny\color{gray},
    stepnumber=1,
    numbersep=5pt,
    frame=single,
    breaklines=true,
    breakatwhitespace=true,
    tabsize=4,
    showstringspaces=false
}

\title{ {{- title -}} }
{% if author -%}
\author{ {{- author -}} }
{% endif -%}
\date{ {{- date -}} }

\begin{document}

\maketitle

{% if description -%}
\section{Overview}
{{ description }}
{% endif -%}

\section{Source Code}

\lstinputlisting[caption={Generated Code}]{{{ code_filename }}}

{% if plot_paths -%}
\section{Generated Visualizations}

{% for plot_path in plot_paths -%}
\begin{figure}[h]
\centering
\includegraphics[width=0.8\textwidth]{ {{- plot_path.name -}} }
\caption{Generated visualization {% if loop.index > 1 %}{{ loop.index }}{% endif %}}
\label{fig:plot{% if loop.index > 1 %}_{{ loop.index }}{% endif %}}
\end{figure}

{% endfor -%}
{% endif -%}

{% if metadata.execution_time -%}
\section{Execution Details}

\begin{itemize}
\item \textbf{Execution Time}: {{ metadata.execution_time }}
\item \textbf{Generated}: {{ date }}
\item \textbf{Source File}: \texttt{ {{- metadata.filename -}} }
{% if metadata.function_name -%}
\item \textbf{Function}: \texttt{ {{- metadata.function_name -}} }
{% endif -%}
\end{itemize}
{% endif -%}

\end{document}
"""
        
        latex_path = context.output_dir / f"{context.timestamp}_snapshot.tex"
        code_path = context.output_dir / f"{context.timestamp}_code.py"
        
        # Save code to separate file for \lstinputlisting
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(context.code)
        
        # Render LaTeX template
        template = Template(latex_template)
        latex_content = template.render(
            title=context.metadata.get('function_name', 'Code Snapshot'),
            author=context.metadata.get('author'),
            date=context.metadata.get('date', 'Unknown'),
            description=context.metadata.get('description'),
            code_filename=code_path.name,
            plot_paths=context.plot_paths,
            metadata=context.metadata
        )
        
        # Write LaTeX file
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return latex_path


class ExportFormatRegistry:
    """Registry for managing export formats."""
    
    def __init__(self):
        self.formats: Dict[str, ExportFormat] = {}
        self._register_default_formats()
    
    def _register_default_formats(self):
        """Register built-in export formats."""
        self.register_format(HTMLExportFormat())
        self.register_format(MarkdownExportFormat())
        self.register_format(LaTeXExportFormat())
        
        # Register optional formats if dependencies are available
        pdf_format = PDFExportFormat()
        if pdf_format.is_available():
            self.register_format(pdf_format)
        
        notebook_format = JupyterNotebookExportFormat()
        if notebook_format.is_available():
            self.register_format(notebook_format)
    
    def register_format(self, export_format: ExportFormat):
        """Register an export format."""
        self.formats[export_format.name] = export_format
    
    def get_format(self, name: str) -> Optional[ExportFormat]:
        """Get an export format by name."""
        return self.formats.get(name)
    
    def list_available_formats(self) -> List[str]:
        """List all available export formats."""
        return [name for name, fmt in self.formats.items() if fmt.is_available()]
    
    def list_all_formats(self) -> List[str]:
        """List all registered formats (including unavailable ones)."""
        return list(self.formats.keys())
    
    def export_to_formats(self, context: ExportContext, 
                         formats: List[str]) -> Dict[str, Path]:
        """
        Export snapshot to multiple formats.
        
        Args:
            context: Export context
            formats: List of format names to export to
            
        Returns:
            Dict mapping format names to exported file paths
        """
        results = {}
        
        for format_name in formats:
            export_format = self.get_format(format_name)
            if not export_format:
                warnings.warn(f"Export format '{format_name}' not available")
                continue
            
            if not export_format.is_available():
                warnings.warn(
                    f"Export format '{format_name}' requires: {', '.join(export_format.dependencies)}"
                )
                continue
            
            try:
                exported_path = export_format.export(context)
                results[format_name] = exported_path
            except Exception as e:
                warnings.warn(f"Failed to export to {format_name}: {e}")
        
        return results


# Global registry instance
_global_export_registry = ExportFormatRegistry()


def get_export_registry() -> ExportFormatRegistry:
    """Get the global export format registry."""
    return _global_export_registry


def register_custom_format(export_format: ExportFormat):
    """Register a custom export format."""
    _global_export_registry.register_format(export_format)


def export_snapshot(code: str, plot_paths: List[Path], metadata: Dict[str, Any],
                   timestamp: str, output_dir: Path, 
                   formats: List[str] = None) -> Dict[str, Path]:
    """
    Export snapshot to specified formats.
    
    Args:
        code: Source code to export
        plot_paths: List of plot file paths
        metadata: Snapshot metadata
        timestamp: Timestamp string
        output_dir: Output directory
        formats: List of format names (defaults to ['html'])
        
    Returns:
        Dict mapping format names to exported file paths
    """
    if formats is None:
        formats = ['html']
    
    context = ExportContext(
        code=code,
        plot_paths=plot_paths,
        metadata=metadata,
        timestamp=timestamp,
        output_dir=output_dir
    )
    
    return _global_export_registry.export_to_formats(context, formats)


def list_export_formats() -> Dict[str, Dict[str, Any]]:
    """
    List all available export formats with their details.
    
    Returns:
        Dict with format details including availability and dependencies
    """
    registry = get_export_registry()
    format_info = {}
    
    for name, fmt in registry.formats.items():
        format_info[name] = {
            'available': fmt.is_available(),
            'file_extension': fmt.file_extension,
            'mime_type': fmt.mime_type,
            'dependencies': fmt.dependencies
        }
    
    return format_info