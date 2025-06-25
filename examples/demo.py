"""
Demo script showcasing snapshotplot functionality.

This script demonstrates both decorator and context manager usage
with various matplotlib plotting examples.
"""

import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for headless operation
import numpy as np
import matplotlib.pyplot as plt
from snapshotplot import snapshot


@snapshot(
    output_dir="demo_outputs",
    title="Sine Wave Analysis",
    author="Demo User",
    notes="Simple sine wave with grid and labels"
)
def plot_sine_wave():
    """Create a simple sine wave plot."""
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
    plt.title("Sine Wave Function", fontsize=16)
    plt.xlabel("x", fontsize=12)
    plt.ylabel("sin(x)", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()


@snapshot(
    output_dir="demo_outputs",
    title="Multiple Functions Comparison",
    author="Demo User",
    notes="Comparing different mathematical functions"
)
def plot_multiple_functions():
    """Plot multiple mathematical functions for comparison."""
    x = np.linspace(-3, 3, 200)
    
    plt.figure(figsize=(12, 8))
    plt.plot(x, x**2, 'r-', linewidth=2, label='x²')
    plt.plot(x, x**3, 'g-', linewidth=2, label='x³')
    plt.plot(x, np.exp(x), 'b-', linewidth=2, label='e^x')
    plt.plot(x, np.log(np.abs(x) + 1), 'm-', linewidth=2, label='log(|x| + 1)')
    
    plt.title("Mathematical Functions Comparison", fontsize=16)
    plt.xlabel("x", fontsize=12)
    plt.ylabel("y", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.ylim(-5, 10)
    plt.tight_layout()


@snapshot(
    output_dir="demo_outputs",
    title="Scatter Plot with Random Data",
    author="Demo User",
    notes="Scatter plot demonstrating random data visualization"
)
def plot_scatter_data():
    """Create a scatter plot with random data."""
    np.random.seed(42)  # For reproducible results
    
    x = np.random.normal(0, 1, 100)
    y = np.random.normal(0, 1, 100)
    colors = np.random.rand(100)
    sizes = 1000 * np.random.rand(100)
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
    plt.colorbar(scatter, label='Color Value')
    
    plt.title("Random Scatter Plot", fontsize=16)
    plt.xlabel("X Coordinate", fontsize=12)
    plt.ylabel("Y Coordinate", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()


def demo_context_manager():
    """Demonstrate context manager usage."""
    print("Running context manager demo...")
    
    with snapshot(
        output_dir="demo_outputs",
        title="Context Manager Demo",
        author="Demo User",
        notes="This was created using the context manager approach"
    ):
        # Create a complex plot
        t = np.linspace(0, 10, 1000)
        signal = np.sin(2*np.pi*t) + 0.5*np.sin(4*np.pi*t) + 0.3*np.random.randn(1000)
        
        plt.figure(figsize=(12, 8))
        
        # Main signal
        plt.subplot(2, 1, 1)
        plt.plot(t, signal, 'b-', linewidth=1, alpha=0.7)
        plt.title("Complex Signal Analysis", fontsize=16)
        plt.ylabel("Amplitude", fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # FFT
        plt.subplot(2, 1, 2)
        fft_vals = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(t), t[1] - t[0])
        plt.plot(freqs[:len(freqs)//2], np.abs(fft_vals[:len(fft_vals)//2]), 'r-', linewidth=2)
        plt.title("Frequency Spectrum", fontsize=14)
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel("Magnitude", fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()


def demo_subplots():
    """Demonstrate subplot functionality."""
    print("Running subplot demo...")
    
    with snapshot(
        output_dir="demo_outputs",
        title="Subplot Demonstration",
        author="Demo User",
        notes="Multiple subplots in a single figure"
    ):
        x = np.linspace(0, 4*np.pi, 200)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Subplot Demonstration", fontsize=16)
        
        # Plot 1: Sine
        axes[0, 0].plot(x, np.sin(x), 'b-', linewidth=2)
        axes[0, 0].set_title("Sine Function")
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Cosine
        axes[0, 1].plot(x, np.cos(x), 'r-', linewidth=2)
        axes[0, 1].set_title("Cosine Function")
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Tangent
        axes[1, 0].plot(x, np.tan(x), 'g-', linewidth=2)
        axes[1, 0].set_title("Tangent Function")
        axes[1, 0].set_ylim(-5, 5)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Combined
        axes[1, 1].plot(x, np.sin(x), 'b-', linewidth=2, label='sin(x)')
        axes[1, 1].plot(x, np.cos(x), 'r-', linewidth=2, label='cos(x)')
        axes[1, 1].set_title("Combined Functions")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()


def main():
    """Run all demo functions."""
    print("🚀 Starting SnapshotPlot Demo")
    print("=" * 50)
    
    # Run decorator examples
    print("\n1. Running decorator examples...")
    plot_sine_wave()
    plt.close()
    plot_multiple_functions()
    plt.close()
    plot_scatter_data()
    plt.close()
    
    # Run context manager examples
    print("\n2. Running context manager examples...")
    demo_context_manager()
    plt.close()
    demo_subplots()
    plt.close()
    
    print("\n✅ Demo completed!")
    print("Check the 'demo_outputs' directory for generated snapshots.")
    print("Each snapshot contains:")
    print("  - Source code (.py)")
    print("  - Plot image (.png)")
    print("  - HTML documentation (.html)")


if __name__ == "__main__":
    main() 