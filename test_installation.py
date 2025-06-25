#!/usr/bin/env python3
"""
Quick test script to verify snapshotplot installation and basic functionality.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from snapshotplot import snapshot, SnapshotContext
        print("✅ Main package imports successful")
    except ImportError as e:
        print(f"❌ Main package import failed: {e}")
        return False
    
    try:
        from snapshotplot.timestamp import get_timestamp
        from snapshotplot.code_capture import get_calling_info
        from snapshotplot.file_manager import create_output_directory
        from snapshotplot.html_writer import generate_html
        from snapshotplot.utils import save_current_plot
        print("✅ All submodules import successful")
    except ImportError as e:
        print(f"❌ Submodule import failed: {e}")
        return False
    
    return True


def test_basic_functionality():
    """Test basic functionality without matplotlib."""
    print("\nTesting basic functionality...")
    
    try:
        from snapshotplot.timestamp import get_timestamp, reset_timestamp
        from snapshotplot.code_capture import get_calling_info
        
        # Test timestamp
        reset_timestamp()
        timestamp = get_timestamp()
        print(f"✅ Timestamp generation: {timestamp}")
        
        # Test code capture
        info = get_calling_info()
        print(f"✅ Code capture: {info['function_name']} in {info['filename']}")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def test_matplotlib_integration():
    """Test matplotlib integration if available."""
    print("\nTesting matplotlib integration...")
    
    try:
        import matplotlib
        import matplotlib.pyplot as plt
        print(f"✅ Matplotlib available: {matplotlib.__version__}")
        
        # Test basic plot creation
        plt.figure()
        plt.plot([1, 2, 3], [1, 4, 9])
        plt.close()  # Clean up
        print("✅ Basic matplotlib functionality works")
        
        return True
    except ImportError:
        print("⚠️  Matplotlib not available - skipping integration test")
        return True
    except Exception as e:
        print(f"❌ Matplotlib integration test failed: {e}")
        return False


def test_dependencies():
    """Test that all dependencies are available."""
    print("\nTesting dependencies...")
    
    dependencies = [
        ('matplotlib', 'matplotlib'),
        ('jinja2', 'jinja2'),
        ('pygments', 'pygments')
    ]
    
    all_available = True
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name} available")
        except ImportError:
            print(f"❌ {package_name} not available")
            all_available = False
    
    return all_available


def main():
    """Run all tests."""
    print("🧪 SnapshotPlot Installation Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_matplotlib_integration,
        test_dependencies
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    if all(results):
        print("🎉 All tests passed! SnapshotPlot is ready to use.")
        print("\nTo test the full functionality, run:")
        print("  python examples/demo.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 