#!/usr/bin/env python3
"""
Demo script to show how SnapshotPlot Jupyter integration works.

This script demonstrates the core functionality without requiring a full Jupyter environment.
"""

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add the current directory to path so we can import snapshotplot
sys.path.insert(0, '/Users/dryan/GitHub/snapshotplot')

def demo_notebook_detection():
    """Demonstrate notebook detection functionality."""
    print("=== Testing Notebook Detection ===")
    
    try:
        from snapshotplot.jupyter import is_notebook, get_notebook_info
        
        print(f"Running in notebook: {is_notebook()}")
        notebook_info = get_notebook_info()
        print(f"Notebook info: {notebook_info}")
        
    except ImportError as e:
        print(f"Import error (expected in non-Jupyter environment): {e}")
    
    print()

def demo_magic_command_simulation():
    """Simulate what happens when magic commands are used."""
    print("=== Simulating Magic Command Functionality ===")
    
    # Simulate cell code that would be captured
    cell_code = '''
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(8, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.title('Sine Wave Demo')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.savefig('demo_plot.png')  # Save instead of show to avoid hanging
plt.close()
'''
    
    print("Cell code that would be captured:")
    print("-" * 40)
    print(cell_code.strip())
    print("-" * 40)
    
    # Execute the code to create a plot
    exec(cell_code)
    
    # Now demonstrate what the magic command would do
    print("\nWhat %%snapshot magic would capture:")
    print("- Cell source code ✓")
    print("- Generated plot ✓") 
    print("- Metadata (timestamp, notebook name, etc.) ✓")
    print("- Create HTML documentation ✓")
    
    print()

def demo_context_manager():
    """Demonstrate the notebook_snapshot context manager."""
    print("=== Testing Notebook Context Manager ===")
    
    try:
        from snapshotplot.jupyter import notebook_snapshot
        
        print("Using notebook_snapshot context manager...")
        
        # This will fall back to regular snapshot since we're not in a notebook
        with notebook_snapshot(title="Demo Plot", author="Demo User"):
            # Generate some data
            x = np.linspace(0, 10, 50)
            y = x**2
            
            # Create plot
            plt.figure(figsize=(8, 6))
            plt.plot(x, y, 'r-', linewidth=2, marker='o', markersize=4)
            plt.title('Quadratic Function Demo')
            plt.xlabel('x')
            plt.ylabel('x²')
            plt.grid(True, alpha=0.3)
            plt.savefig('demo_plot2.png')  # Save instead of show
            plt.close()
        
        print("Context manager completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def demo_magic_class_structure():
    """Show the structure of the magic commands class."""
    print("=== Magic Commands Class Structure ===")
    
    try:
        from snapshotplot.jupyter import SnapshotMagics
        
        # Show available methods
        magic_methods = [method for method in dir(SnapshotMagics) 
                        if not method.startswith('_') and callable(getattr(SnapshotMagics, method))]
        
        print("Available magic methods:")
        for method in magic_methods:
            print(f"  - {method}")
        
        print("\nMagic command usage:")
        print("  Line magic:  %snapshot -t 'Title' -a 'Author'")
        print("  Cell magic:  %%snapshot -t 'Title' -a 'Author'")
        print("               [your plotting code here]")
        
    except ImportError as e:
        print(f"Could not import SnapshotMagics: {e}")
    
    print()

def show_generated_files():
    """Show what files would be generated."""
    print("=== Generated Files Demo ===")
    
    # Look for any snapshot directories that were created
    import glob
    
    snapshot_dirs = glob.glob("snapshot_*")
    if snapshot_dirs:
        print(f"Found {len(snapshot_dirs)} snapshot directories:")
        for dir_name in snapshot_dirs[:3]:  # Show first 3
            print(f"  📁 {dir_name}/")
            files = glob.glob(f"{dir_name}/*")
            for file_path in files:
                file_name = os.path.basename(file_path)
                if file_name.endswith('.html'):
                    print(f"    📄 {file_name} (HTML documentation)")
                elif file_name.endswith('.png'):
                    print(f"    🖼️  {file_name} (Plot image)")
                elif file_name.endswith('.py'):
                    print(f"    🐍 {file_name} (Source code)")
    else:
        print("No snapshot directories found (this is normal for the demo)")
    
    print()

def main():
    """Run all demos."""
    print("🔬 SnapshotPlot Jupyter Integration Demo")
    print("=" * 50)
    print()
    
    # Set matplotlib to non-interactive mode for demo
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    plt.ioff()
    
    # Run all demo functions
    demo_notebook_detection()
    demo_magic_command_simulation()
    demo_context_manager()
    demo_magic_class_structure() 
    show_generated_files()
    
    print("✅ Demo completed!")
    print("\nTo use in actual Jupyter notebooks:")
    print("1. %load_ext snapshotplot")
    print("2. %%snapshot -t 'Your Title'")
    print("3. [your plotting code]")

if __name__ == "__main__":
    main()