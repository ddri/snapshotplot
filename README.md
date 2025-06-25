# SnapShotPlot 📸📊

Capture Python code, Matplotlib plots, and HTML documentation in one step with automatic timestamping and organization.

Ever run into this?

"Cool plot... where's the code that made it?"
"You made a mistake here, this other plot a few runs back was the correct one."
"Uhh... I think I overwrote it... maybe version 12_final_final_really_final.py?"


Yeah. Same.

snapshotplot was born out of one too many late-night research plot reviews where the code was somewhere, but no one could say where. I got tired of asking "how did you generate this?" and getting blank stares.

This package automatically takes a snapshot of your code and the plot every time you run it—HTML, code, and image saved, timestamped, and organized like a sane person lives here.

You get reproducibility without thinking about it. Your future self (and your collaborators) will thank you.

Just wrap your code with the snapshot context manager and keep shipping.

Because science shouldn't involve detective work.

![SnapshotPlot HTML Output](assets/screenshot.png)

## Features

- **🔄 Decorator & Context Manager Support**: Use as `@snapshot()` or `with snapshot():`
- **⏰ Unified Timestamping**: Single UTC timestamp per snapshot run
- **📁 Auto-Organization**: Creates timestamped folders with all outputs
- **🎨 HTML Documentation**: Beautiful, syntax-highlighted HTML with embedded plots
- **🔧 Zero Configuration**: Works out of the box with sensible defaults
- **🚀 Non-Intrusive**: Runs silently in the background

## Quick Start

### Installation

```bash
pip install snapshotplot
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
```

#### As a Context Manager

```python
from snapshotplot import snapshot
import matplotlib.pyplot as plt
import numpy as np

with snapshot():
    x = np.linspace(0, 10, 100)
    y = x**2
    plt.plot(x, y)
    plt.title("Quadratic Function")
    plt.xlabel("x")
    plt.ylabel("y = x²")
    plt.show()
```

## Output Structure

Each snapshot creates a folder structure like this:

```
snapshot_<filename>/
├── 20241201_143022_123_code.py       # Raw source code
├── 20241201_143022_123_plot.png      # Saved plot image
└── 20241201_143022_123_snapshot.html # HTML documentation
```

The HTML file contains:
- **Metadata**: Filename, function name, timestamp
- **Syntax-highlighted code**: Your Python code with proper formatting
- **Embedded plot**: The matplotlib figure directly in the HTML
- **Clean styling**: Professional, readable layout

## HTML Example

Here's what the generated HTML documentation looks like:

![SnapshotPlot HTML Output](assets/screenshot.png)

The output includes:
- **Dark mode interface** for easy reading
- **Side-by-side layout** with code and plot
- **Syntax-highlighted Python code**
- **Embedded plot images**
- **Responsive design** for mobile and desktop

## Configuration Options

```python
@snapshot(
    output_dir="my_snapshots",      # Custom output directory
    code_format="html",            # Code format in HTML
    title="My Analysis",           # Custom title for HTML
    author="Data Scientist",       # Author metadata
    notes="Important findings"     # Additional notes
)
def my_analysis():
    # Your code here
    pass
```

## Advanced Usage

### Custom Output Directory

```python
@snapshot(output_dir="research_outputs")
def research_plot():
    # Your research code
    pass
```

### With Metadata

```python
@snapshot(
    title="Sales Analysis Q4",
    author="Analytics Team",
    notes="Key insights from quarterly data"
)
def sales_analysis():
    # Your analysis code
    pass
```

### Context Manager with Configuration

```python
with snapshot(output_dir="experiments", title="A/B Test Results"):
    # Your experimental code
    pass
```

## Requirements

- Python 3.8+
- matplotlib >= 3.5.0
- jinja2 >= 3.0.0
- pygments >= 2.10.0

## Development

### Installation for Development

```bash
git clone https://github.com/snapshotplot/snapshotplot.git
cd snapshotplot
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black snapshotplot/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Roadmap

- [ ] Support for Plotly and Altair
- [ ] Markdown export option
- [ ] Multiple plot gallery
- [ ] CLI tool for batch processing
- [ ] Jupyter notebook integration 
