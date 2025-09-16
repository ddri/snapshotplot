#!/usr/bin/env python3
"""
Quick test script to verify snapshotplot installation and basic functionality.
"""

import sys
import os
import pytest

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    # Main package imports
    from snapshotplot import snapshot, SnapshotContext  # noqa: F401
    print("✅ Main package imports successful")
    
    # Submodule imports
    from snapshotplot.core.timestamp import get_timestamp  # noqa: F401
    from snapshotplot.core.code_capture import get_calling_info  # noqa: F401
    from snapshotplot.core.file_manager import create_output_directory  # noqa: F401
    from snapshotplot.core.html_writer import generate_html  # noqa: F401
    from snapshotplot.core.utils import save_current_plot  # noqa: F401
    print("✅ All submodules import successful")


def test_basic_functionality():
    """Test basic functionality without matplotlib."""
    print("\nTesting basic functionality...")
    
    from snapshotplot.core.timestamp import get_timestamp, reset_timestamp
    from snapshotplot.core.code_capture import get_calling_info
    
    # Test timestamp
    reset_timestamp()
    timestamp = get_timestamp()
    print(f"✅ Timestamp generation: {timestamp}")
    assert isinstance(timestamp, str)
    assert len(timestamp) >= 15
    
    # Test code capture
    info = get_calling_info()
    print(f"✅ Code capture: {info['function_name']} in {info['filename']}")
    assert 'function_name' in info and 'filename' in info and 'source_code' in info


def test_matplotlib_integration():
    """Test matplotlib integration if available."""
    print("\nTesting matplotlib integration...")
    
    matplotlib = pytest.importorskip("matplotlib")
    import matplotlib.pyplot as plt
    print(f"✅ Matplotlib available: {matplotlib.__version__}")
    
    # Test basic plot creation
    plt.figure()
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.close()  # Clean up
    print("✅ Basic matplotlib functionality works")


def test_dependencies():
    """Test that all dependencies are available."""
    print("\nTesting dependencies...")
    
    dependencies = [
        ('matplotlib', 'matplotlib'),
        ('jinja2', 'jinja2'),
        ('pygments', 'pygments')
    ]
    
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package_name} available")
        except ImportError:
            pytest.fail(f"{package_name} not available")


def main():
    """Run all tests as a script (optional)."""
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
        try:
            test()
            results.append(True)
        except pytest.skip.Exception:
            print("⏭️  Skipped a test")
            results.append(True)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
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
