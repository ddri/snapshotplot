---
title: Jupyter Notebook Integration
description: Complete guide to using SnapshotPlot in Jupyter notebooks with magic commands
layout: default
permalink: /jupyter/
---

# Jupyter Notebook Integration

SnapshotPlot provides seamless integration with Jupyter notebooks through IPython magic commands, enabling you to capture and document your analysis workflow with zero overhead.

## Quick Start

```python
# 1. Load the extension (once per notebook)
%load_ext snapshotplot

# 2. Use cell magic to capture analysis
%%snapshot -t "Customer Analysis" -a "Data Science Team"
import matplotlib.pyplot as plt
import pandas as pd

# Your analysis code
df = pd.read_csv('data.csv')
plt.figure(figsize=(10, 6))
plt.hist(df['revenue'], bins=30)
plt.title('Revenue Distribution')
plt.show()
```

## Magic Commands

### Cell Magic (`%%snapshot`)

Capture an entire cell's code and output - the most common usage pattern:

```python
%%snapshot -t "Market Segmentation" -a "Analytics Team" --tags ml clustering
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

# Perform clustering analysis
data = np.random.rand(100, 2)
kmeans = KMeans(n_clusters=3)
clusters = kmeans.fit_predict(data)

# Visualize results
plt.figure(figsize=(8, 6))
plt.scatter(data[:, 0], data[:, 1], c=clusters, cmap='viridis')
plt.title('Customer Segments')
plt.xlabel('Feature 1')
plt.ylabel('Feature 2')
plt.colorbar(label='Cluster')
plt.show()
```

### Line Magic (`%snapshot`)

Capture the previous cell's output - useful for retroactive documentation:

```python
# First cell: Create your analysis
plt.figure(figsize=(10, 6))
plt.plot(time_series_data)
plt.title('Sales Trend Over Time')
plt.show()

# Second cell: Capture it with metadata
%snapshot -t "Q4 Sales Trend" -a "Sales Team" --tags quarterly sales --description "Shows strong growth in Q4"
```

## Magic Command Arguments

All magic commands support comprehensive metadata and configuration options:

| Argument | Short | Description | Example |
|----------|-------|-------------|---------|
| `--title` | `-t` | Snapshot title | `-t "Analysis Title"` |
| `--author` | `-a` | Author name | `-a "Data Team"` |
| `--notes` | `-n` | Additional notes | `-n "Key findings"` |
| `--tags` | | Space-separated tags | `--tags ml analysis` |
| `--description` | | Detailed description | `--description "Model evaluation"` |
| `--collection` | | Collection name | `--collection research` |
| `--output-dir` | `-o` | Custom output directory | `-o custom_snapshots` |
| `--dpi` | | Plot resolution | `--dpi 300` |
| `--site` | | Site directory | `--site ../blog` |
| `--auto-build` | | Auto-build site | `--auto-build` |

### Full Example

```python
%%snapshot -t "Final Model Results" \
           -a "ML Team" \
           -n "Production model evaluation" \
           --tags model evaluation production \
           --description "Performance metrics for the final customer churn model" \
           --collection "ml-models" \
           --site "../research-blog" \
           --auto-build
           
# Your model evaluation code
from sklearn.metrics import classification_report, confusion_matrix
y_pred = model.predict(X_test)

plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Model Performance')
plt.show()

print(classification_report(y_test, y_pred))
```

## Context Manager

Use the notebook-aware context manager for programmatic control:

```python
from snapshotplot import notebook_snapshot

# Basic usage
with notebook_snapshot(title="Experiment Results"):
    run_experiment()
    plot_results()
    plt.show()

# With full configuration
with notebook_snapshot(
    title="A/B Test Analysis",
    author="Product Team", 
    tags=["ab-test", "conversion"],
    collection="experiments",
    site="../product-blog"
):
    analyze_ab_test()
    plot_conversion_rates()
    plt.show()
```

## Real-World Workflow

Here's how to integrate SnapshotPlot into a typical data science workflow:

```python
# === NOTEBOOK SETUP ===
%load_ext snapshotplot
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# === EXPLORATORY DATA ANALYSIS ===
# Regular cells for exploration (no snapshot needed)
df = pd.read_csv('customer_data.csv')
df.info()
df.describe()

# === KEY INSIGHTS (Capture with snapshot) ===
%%snapshot -t "Customer Demographics Overview" -a "Data Science Team" --tags demographics eda
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
df['age'].hist(bins=20)
plt.title('Age Distribution')

plt.subplot(1, 3, 2) 
df['income'].hist(bins=20)
plt.title('Income Distribution')

plt.subplot(1, 3, 3)
sns.countplot(data=df, x='segment')
plt.title('Customer Segments')

plt.tight_layout()
plt.show()

# === MODELING (More exploration) ===
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# === MODEL RESULTS (Capture with snapshot) ===
%%snapshot -t "Model Performance Evaluation" --tags modeling evaluation --collection research
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# Evaluate model
y_pred = model.predict(X_test)

# Plot confusion matrix
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.show()

print("Classification Report:")
print(classification_report(y_test, y_pred))

# === FINAL INSIGHTS (Capture for presentation) ===
%%snapshot -t "Business Impact Analysis" -a "Data Science Team" \
           --description "Revenue impact of customer segmentation model" \
           --tags business-impact revenue --collection presentations \
           --site "../executive-dashboard" --auto-build

# Calculate business impact
plot_revenue_impact_by_segment()
plt.show()
```

## Generated Output

Each snapshot creates three files with consistent naming:

```
Project/
├── my_analysis.ipynb
└── snapshot_my_analysis/
    ├── 20240718_143022_001_code.py      # Cell source code
    ├── 20240718_143022_001_plot.png     # Matplotlib figure
    ├── 20240718_143022_001_snapshot.html # HTML documentation
    ├── 20240718_143155_002_code.py      # Next snapshot
    ├── 20240718_143155_002_plot.png
    └── 20240718_143155_002_snapshot.html
```

## HTML Documentation Features

The generated HTML documentation includes:

- **Notebook Metadata**: Name, kernel info, execution timestamp
- **Syntax-Highlighted Code**: Beautiful Python code formatting
- **Embedded Plots**: High-resolution matplotlib figures
- **User Metadata**: Title, author, tags, and notes
- **Responsive Design**: Mobile and desktop friendly
- **Dark Mode Theme**: Easy on the eyes for long reading sessions
- **Professional Styling**: Ready for sharing with stakeholders

## Multiple Visualization Libraries

SnapshotPlot works with all major visualization libraries in Jupyter:

### Matplotlib (Default)
```python
%%snapshot -t "Matplotlib Visualization"
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 2])
plt.title('Basic Line Plot')
plt.show()
```

### Plotly (Interactive)
```python
%%snapshot -t "Interactive Plotly Chart" --backend plotly
import plotly.graph_objects as go
fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[1, 4, 2]))
fig.update_layout(title='Interactive Plot')
fig.show()
```

### Seaborn (Statistical)
```python
%%snapshot -t "Statistical Visualization"
import seaborn as sns
import pandas as pd

data = pd.DataFrame({'x': range(10), 'y': np.random.randn(10)})
sns.scatterplot(data=data, x='x', y='y')
plt.title('Seaborn Scatter Plot')
plt.show()
```

## Site Integration

For teams maintaining research blogs or documentation sites, SnapshotPlot can automatically integrate with static site generators:

```python
%%snapshot -t "Quarterly Results" \
           --site "../research-blog" \
           --collection "quarterly-reports" \
           --auto-build

# This will:
# 1. Create the snapshot files
# 2. Copy them to your site's collection directory  
# 3. Generate site metadata
# 4. Build the static site
```

## Environment Detection

You can programmatically detect if code is running in a notebook:

```python
from snapshotplot import is_notebook

if is_notebook():
    print("Running in Jupyter - magic commands available!")
    %load_ext snapshotplot
else:
    print("Running in regular Python - using context managers")
    from snapshotplot import snapshot
```

## Best Practices

1. **Load Once**: Run `%load_ext snapshotplot` once at the beginning of your notebook
2. **Meaningful Titles**: Use descriptive titles that will make sense months later
3. **Tag Everything**: Use consistent tags to organize your analysis across notebooks
4. **Capture Key Steps**: Not every cell needs a snapshot - focus on important insights
5. **Team Consistency**: Establish naming conventions for titles, authors, and tags
6. **Regular Review**: Generated HTML files are perfect for team reviews and presentations

## Troubleshooting

### Extension Not Loading
```python
# If %load_ext fails, try:
%reload_ext snapshotplot

# Or install with jupyter support:
# pip install snapshotplot[jupyter]
```

### Magic Command Not Found
```python
# Verify extension is loaded:
%lsmagic | grep snapshot

# Should show %%snapshot and %snapshot
```

### Plots Not Captured
```python
# Ensure plt.show() is called in the cell
plt.plot([1, 2, 3])
plt.show()  # Required for capture

# For Plotly, ensure fig.show() is called
fig.show()  # Required for Plotly capture
```

### Permission Errors
```bash
# Check write permissions to snapshot directory
ls -la snapshots/

# Create directory if needed
mkdir -p snapshots
chmod 755 snapshots
```

The Jupyter integration makes SnapshotPlot incredibly powerful for data science workflows, providing seamless documentation without disrupting your analysis flow.