---
title: Getting Started with SnapshotPlot
description: Learn how to capture and document your Python analysis with SnapshotPlot
layout: default
permalink: /getting-started/
---

# Getting Started with SnapshotPlot

SnapshotPlot automatically captures your Python code, visualizations, and documentation in one step with automatic timestamping and organization.

## Quick Start

### Installation

Choose your workflow and install the appropriate features:

```bash
# Solo Researcher (Core Only)
pip install snapshotplot

# Data Science Team (Core + Jupyter + Multi-library support)  
pip install snapshotplot[jupyter]

# Research Organization (Core + Site Generator + Export formats)
pip install snapshotplot[site]

# All Features
pip install snapshotplot[all]
```

### Basic Usage

#### As a Decorator

```python
from snapshotplot import snapshot
import matplotlib.pyplot as plt
import numpy as np

@snapshot()
def create_sine_wave():
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)
    plt.plot(x, y)
    plt.title("Sine Wave")
    plt.grid(True)
    plt.show()

create_sine_wave()
```

#### As a Context Manager

```python
with snapshot():
    x = np.linspace(0, 10, 100)
    y = x**2
    plt.plot(x, y)
    plt.title("Quadratic Function")
    plt.xlabel("x")
    plt.ylabel("y = x²")
    plt.show()
```

## Enhanced Features

### Multiple Visualization Libraries

```python
# Use Plotly for interactive visualizations
@snapshot(backend='plotly', title='Interactive Analysis')
def create_interactive_plot():
    import plotly.graph_objects as go
    fig = go.Figure(data=go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]))
    fig.show()

# Use Altair for statistical visualizations
@snapshot(backend='altair', title='Statistical Visualization')
def create_altair_plot():
    import altair as alt
    import pandas as pd
    
    data = pd.DataFrame({'x': [1, 2, 3, 4], 'y': [1, 4, 2, 3]})
    chart = alt.Chart(data).mark_circle(size=100).encode(x='x', y='y')
    chart.show()
```

### Multiple Export Formats

```python
@snapshot(
    title='Research Results',
    export_formats=['html', 'pdf', 'markdown'],
    author='Research Team',
    notes='Comprehensive analysis findings'
)
def research_analysis():
    # Your analysis code
    plt.figure(figsize=(10, 6))
    plt.plot(data)
    plt.title('Research Findings')
    plt.show()
```

### Search and Organization

```python
@snapshot(
    title='Machine Learning Model Evaluation',
    tags=['ml', 'evaluation', 'production'],
    enable_search=True,
    notes='Performance metrics for the customer churn model'
)
def evaluate_model():
    # Create performance plots
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    scores = [0.87, 0.85, 0.89, 0.87]
    
    plt.bar(metrics, scores)
    plt.title('Model Performance')
    plt.ylabel('Score')
    plt.ylim(0, 1)
    plt.show()
```

## Output Structure

Each snapshot creates organized files:

```
snapshots/
└── snapshot_<filename>/
    ├── 20241201_143022_123_code.py       # Raw source code
    ├── 20241201_143022_123_plot.png      # Saved plot image  
    ├── 20241201_143022_123_snapshot.html # HTML documentation
    ├── 20241201_143022_123_snapshot.md   # Markdown export
    └── 20241201_143022_123_snapshot.pdf  # PDF report
```

## Configuration Options

```python
@snapshot(
    # Basic options
    output_dir="my_snapshots",            # Custom output directory
    title="My Analysis",                  # Custom title
    author="Data Scientist",              # Author metadata
    notes="Important findings",           # Additional notes
    
    # Visualization backend
    backend="matplotlib",                 # 'matplotlib', 'plotly', 'altair'
    
    # Export formats
    export_formats=["html", "pdf"],       # Multiple format support
    
    # Search and organization
    enable_search=True,                   # Enable search indexing
    tags=["analysis", "research"],        # Organization tags
    
    # Static site integration
    site="./my-research-site",           # Site directory
    collection="experiments",            # Collection name
    auto_build=True                      # Auto-build static site
)
def my_analysis():
    # Your code here
    pass
```

## Next Steps

- [View Examples](/examples/) - See real-world usage patterns
- [Jupyter Integration](/jupyter/) - Learn about magic commands
- [Static Sites](/static-sites/) - Build searchable documentation websites
- [Search Documentation](/search/) - Organize and find your analysis

## Need Help?

- Check the [GitHub repository](https://github.com/yourusername/snapshotplot) for issues and documentation
- Review the generated HTML files for examples of the output format
- Use the search feature on this site to find specific analysis patterns