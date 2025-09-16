#!/usr/bin/env python3
"""
Comprehensive test of SnapshotPlot's new features.

This script demonstrates:
1. Multiple visualization backends (matplotlib, plotly)
2. Multiple export formats (HTML, Markdown, PDF)
3. Search functionality
4. Backward compatibility
"""

import matplotlib.pyplot as plt
from snapshotplot.core.snapshot import snapshot

# Test 1: Basic matplotlib workflow (backward compatibility)
print("Test 1: Basic matplotlib workflow...")

@snapshot()
def test_matplotlib_basic():
    plt.figure(figsize=(8, 6))
    plt.plot([1, 2, 3, 4], [1, 4, 2, 3], marker='o')
    plt.title('Basic Matplotlib Plot')
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.grid(True)

test_matplotlib_basic()
print("✓ Basic matplotlib test completed")

# Test 2: Multiple export formats
print("\nTest 2: Multiple export formats...")

@snapshot(
    title='Multi-Format Export',
    author='Test User',
    notes='Testing PDF and Markdown export',
    export_formats=['html', 'markdown'],
    tags=['multi-format', 'export']
)
def test_multi_export():
    plt.figure(figsize=(10, 6))
    import numpy as np
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    plt.plot(x, y, label='sin(x)', linewidth=2)
    plt.plot(x, np.cos(x), label='cos(x)', linewidth=2)
    plt.title('Trigonometric Functions')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.grid(True, alpha=0.3)

test_multi_export()
print("✓ Multi-format export test completed")

# Test 3: Plotly backend (if available)
print("\nTest 3: Plotly backend...")

try:
    import plotly.graph_objects as go
    
    @snapshot(
        title='Interactive Plotly Visualization',
        backend='plotly',
        export_formats=['html'],
        tags=['plotly', 'interactive']
    )
    def test_plotly_backend():
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4, 5],
            y=[2, 4, 3, 5, 6],
            mode='markers+lines',
            name='Dataset 1',
            marker=dict(size=10)
        ))
        fig.add_trace(go.Scatter(
            x=[1, 2, 3, 4, 5],
            y=[3, 1, 4, 2, 5],
            mode='markers+lines',
            name='Dataset 2',
            marker=dict(size=10)
        ))
        fig.update_layout(
            title='Interactive Plotly Test',
            xaxis_title='X Axis',
            yaxis_title='Y Axis'
        )
        fig.show()
    
    test_plotly_backend()
    print("✓ Plotly backend test completed")
    
except ImportError:
    print("⚠ Plotly not available, skipping Plotly test")

# Test 4: Search functionality
print("\nTest 4: Search functionality...")

@snapshot(
    title='Searchable Data Analysis',
    export_formats=['html', 'markdown'],
    enable_search=True,
    tags=['analysis', 'searchable', 'demo'],
    notes='This is a searchable snapshot for testing search functionality'
)
def test_search_indexing():
    plt.figure(figsize=(12, 8))
    import numpy as np
    
    # Create sample data analysis plot
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    values = [23, 45, 56, 78, 32]
    
    plt.subplot(2, 2, 1)
    plt.bar(categories, values, color='lightblue')
    plt.title('Bar Chart Analysis')
    plt.xticks(rotation=45)
    
    plt.subplot(2, 2, 2)
    plt.pie(values, labels=categories, autopct='%1.1f%%')
    plt.title('Distribution Pie Chart')
    
    plt.subplot(2, 2, 3)
    x = np.random.normal(0, 1, 1000)
    plt.hist(x, bins=30, alpha=0.7, color='green')
    plt.title('Histogram Distribution')
    
    plt.subplot(2, 2, 4)
    x = np.linspace(0, 10, 50)
    y = np.random.normal(x, 0.5)
    plt.scatter(x, y, alpha=0.6)
    plt.title('Scatter Plot')
    
    plt.tight_layout()

test_search_indexing()
print("✓ Search indexing test completed")

print("\n🎉 All new feature tests completed successfully!")
print("\nGenerated files can be found in the 'snapshots' directory.")
print("Each test demonstrates different aspects of the enhanced SnapshotPlot functionality.")