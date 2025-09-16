# Testing Guide for SnapshotPlot

This guide explains how to test all the new enhanced features of SnapshotPlot.

## Prerequisites

Make sure you have the enhanced SnapshotPlot installed with all optional dependencies:

```bash
pip install -e ".[all]"
```

This installs all optional dependencies for testing the complete functionality.

## Quick Test Suite

### 1. Run Automated Tests
```bash
# Run the full test suite
python -m pytest tests/ -v

# Should show: 10 passed tests
```

### 2. Test New Features Integration
```bash
# Run our comprehensive feature test
python test_new_features.py
```

**Expected Output:**
```
Test 1: Basic matplotlib workflow...
✓ Basic matplotlib test completed

Test 2: Multiple export formats...
✓ Multi-format export test completed

Test 3: Plotly backend...
✓ Plotly backend test completed

Test 4: Search functionality...
✓ Search indexing test completed

🎉 All new feature tests completed successfully!
```

## Individual Feature Testing

### Test 1: Multiple Visualization Backends

**Test Matplotlib (Default):**
```python
from snapshotplot import snapshot
import matplotlib.pyplot as plt

@snapshot(title='Matplotlib Test')
def test_matplotlib():
    plt.plot([1, 2, 3], [1, 4, 2])
    plt.title('Basic Plot')
    plt.show()

test_matplotlib()
```

**Test Plotly Backend:**
```python
import plotly.graph_objects as go
from snapshotplot import snapshot

@snapshot(title='Plotly Test', backend='plotly')
def test_plotly():
    fig = go.Figure(data=go.Bar(x=['A', 'B', 'C'], y=[1, 3, 2]))
    fig.show()

test_plotly()
```

**Expected Results:**
- Files created in `snapshots/snapshot_<filename>/`
- Plotly plots saved as interactive HTML
- Both backends work without conflicts

### Test 2: Multiple Export Formats

```python
@snapshot(
    title='Multi-Format Test',
    export_formats=['html', 'markdown', 'pdf'],
    tags=['test', 'export'],
    notes='Testing all export formats'
)
def test_exports():
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3], 'o-')
    plt.title('Export Format Test')
    plt.show()

test_exports()
```

**Expected Results:**
- `*_snapshot.html` - HTML documentation
- `*_snapshot.md` - Markdown with YAML frontmatter
- `*_snapshot.pdf` - PDF report (if WeasyPrint installed)

### Test 3: Search Functionality

```python
# Create searchable snapshots
@snapshot(
    title='Machine Learning Analysis',
    tags=['ml', 'classification'],
    enable_search=True,
    notes='Testing search indexing functionality'
)
def create_searchable_snapshot():
    plt.figure(figsize=(8, 6))
    plt.bar(['Train', 'Validation', 'Test'], [0.95, 0.87, 0.89])
    plt.title('Model Accuracy')
    plt.ylabel('Accuracy Score')
    plt.show()

create_searchable_snapshot()

# Test search functionality
from snapshotplot.core.search_system import SnapshotSearchManager
from pathlib import Path

search_manager = SnapshotSearchManager(Path('snapshots'))
results = search_manager.search_snapshots('machine learning')
print(f"Found {len(results)} results for 'machine learning'")
```

**Expected Results:**
- Search database created at `snapshots/.snapshotplot/snapshots.db`
- Search returns matching snapshots
- Tags and full-text search work

### Test 4: Static Site with Search

```bash
# Navigate to a site directory (or create one)
cd my-research-plots

# Build enhanced static site
python -c "
from snapshotplot.site.site_generator import SiteGenerator
gen = SiteGenerator('.')
gen.build('docs', verbose=True)
"
```

**Expected Output:**
```
✅ Built index page with N plots
✅ Built collection 'experiments' with N plots
✅ Generated search index with N entries
✅ Built N plots across N collections
```

**Test the Site:**
```bash
# Start local server
cd docs
python -m http.server 8080

# Visit http://localhost:8080
# Try searching for plot titles, tags, or content
```

**Expected Results:**
- Search bar in header works
- Instant search results with thumbnails
- Click results navigate to plot pages
- Mobile-responsive design

### Test 5: CLI Integration

```bash
# Test CLI commands
python -m snapshotplot.cli.cli --help

# Should show available commands:
# - init: Initialize site
# - build: Build static site  
# - serve: Start development server
# - list: List all plots
```

## Troubleshooting

### Common Issues and Solutions

**1. Import Errors**
```bash
# If you see "No module named 'snapshotplot.core'"
pip install -e .

# If you see "No module named 'plotly'"
pip install plotly

# If you see "No module named 'weasyprint'"
pip install weasyprint
```

**2. Search Database Issues**
```bash
# If search doesn't work, check database exists
ls snapshots/.snapshotplot/snapshots.db

# If missing, create a test snapshot with enable_search=True
```

**3. Static Site Issues**
```bash
# If site build fails, check directory structure
ls _layouts/ _includes/

# If search doesn't work, check files exist
ls docs/assets/js/search-index.json
ls docs/assets/js/search.js
```

**4. PDF Export Issues**
```bash
# WeasyPrint installation on macOS
brew install cairo pango gdk-pixbuf libffi

# Then reinstall WeasyPrint
pip install --force-reinstall weasyprint
```

## Performance Testing

### Large Dataset Test
```python
# Test with many snapshots
for i in range(20):
    @snapshot(
        title=f'Performance Test {i}',
        tags=[f'test-{i}', 'performance'],
        enable_search=True
    )
    def perf_test():
        import numpy as np
        x = np.random.randn(1000)
        plt.hist(x, bins=30)
        plt.title(f'Performance Test {i}')
        plt.show()
    
    perf_test()

# Test search performance
search_manager = SnapshotSearchManager(Path('snapshots'))
results = search_manager.search_snapshots('performance')
print(f"Found {len(results)} performance test snapshots")
```

## Integration Testing

### Full Workflow Test
```python
# Complete workflow: Create → Search → Export → Site
from snapshotplot import snapshot
from snapshotplot.site.site_generator import SiteGenerator
import matplotlib.pyplot as plt

# 1. Create analysis snapshots
@snapshot(
    title='Sales Analysis Q4',
    author='Data Team',
    tags=['sales', 'quarterly', 'analysis'],
    export_formats=['html', 'markdown'],
    enable_search=True
)
def sales_analysis():
    months = ['Oct', 'Nov', 'Dec']
    sales = [85000, 92000, 105000]
    plt.bar(months, sales)
    plt.title('Q4 Sales Performance')
    plt.ylabel('Revenue ($)')
    plt.show()

sales_analysis()

# 2. Build searchable static site
site_gen = SiteGenerator('.')
site_gen.build('docs', verbose=True)

# 3. Test search functionality
from snapshotplot.core.search_system import SnapshotSearchManager
search = SnapshotSearchManager(Path('snapshots'))
results = search.search_snapshots('sales')

print(f"✅ Created snapshots: {len(results)} found")
print(f"✅ Built static site with search")
print(f"✅ Integration test complete!")
```

## Success Criteria

**✅ All Tests Pass When:**
1. Automated test suite shows 10/10 passing
2. All visualization backends work (matplotlib, plotly)
3. Multiple export formats generate files
4. Search finds and ranks results correctly
5. Static site builds with working client-side search
6. CLI commands execute without errors
7. No warnings or errors in normal operation

**🎯 Ready for Production When:**
- All success criteria met
- Performance acceptable with 100+ snapshots
- Static site search works on mobile
- Documentation matches implemented features

## Need Help?

If tests fail or you encounter issues:

1. **Check Dependencies**: Run `pip list` and verify all required packages installed
2. **Check Versions**: Ensure Python 3.9+ and package versions meet requirements
3. **Check File Permissions**: Ensure write access to snapshot directories
4. **Check Logs**: Look for warnings/errors in console output
5. **Start Fresh**: Try with a clean directory and simple test case

The test suite is designed to be comprehensive yet easy to run. Most issues are dependency-related and resolve with proper installation.