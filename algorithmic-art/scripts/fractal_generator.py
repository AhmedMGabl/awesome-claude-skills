#!/usr/bin/env python3
"""
Fractal and Algorithmic Art Generator
Demonstrates various generative art techniques
"""

import numpy as np
from PIL import Image
import colorsys


def generate_mandelbrot(width=800, height=600, max_iter=256):
    """
    Generate a Mandelbrot set fractal
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        max_iter: Maximum iterations for convergence test
    
    Returns:
        PIL Image of the Mandelbrot set
    """
    # Define the complex plane bounds
    xmin, xmax = -2.5, 1.0
    ymin, ymax = -1.25, 1.25
    
    # Create coordinate arrays
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    
    # Initialize the output array
    Z = np.zeros_like(C)
    M = np.zeros(C.shape)
    
    # Iterate the Mandelbrot equation
    for i in range(max_iter):
        # Calculate which points haven't diverged
        mask = np.abs(Z) <= 2
        # Update Z for non-diverged points
        Z[mask] = Z[mask]**2 + C[mask]
        # Record iteration count
        M[mask] = i
    
    # Normalize and create colorful image
    M = M / max_iter
    
    # Create RGB image with smooth coloring
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            # Convert iteration count to HSV color
            hue = M[i, j]
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0 if M[i, j] < 1.0 else 0)
            img_array[i, j] = [int(c * 255) for c in rgb]
    
    return Image.fromarray(img_array)


def generate_julia_set(c_real=-0.7, c_imag=0.27, width=800, height=600, max_iter=256):
    """
    Generate a Julia set fractal
    
    Args:
        c_real: Real part of the complex constant
        c_imag: Imaginary part of the complex constant
        width: Image width in pixels
        height: Image height in pixels
        max_iter: Maximum iterations
    
    Returns:
        PIL Image of the Julia set
    """
    c = complex(c_real, c_imag)
    
    # Define bounds
    xmin, xmax = -2.0, 2.0
    ymin, ymax = -1.5, 1.5
    
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    M = np.zeros(Z.shape)
    
    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + c
        M[mask] = i
    
    M = M / max_iter
    
    # Rainbow gradient coloring
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            if M[i, j] < 1.0:
                hue = M[i, j] * 360
                rgb = colorsys.hsv_to_rgb(hue / 360, 0.8, 1.0)
                img_array[i, j] = [int(c * 255) for c in rgb]
    
    return Image.fromarray(img_array)


def generate_voronoi_pattern(num_points=50, width=800, height=600, seed=None):
    """
    Generate a Voronoi diagram pattern
    
    Args:
        num_points: Number of seed points
        width: Image width
        height: Image height
        seed: Random seed for reproducibility
    
    Returns:
        PIL Image of Voronoi diagram
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate random seed points
    points = np.random.rand(num_points, 2)
    points[:, 0] *= width
    points[:, 1] *= height
    
    # Create image array
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Assign colors to each point
    colors = []
    for i in range(num_points):
        hue = i / num_points
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        colors.append([int(c * 255) for c in rgb])
    
    # For each pixel, find nearest point
    for y in range(height):
        for x in range(width):
            distances = np.sqrt((points[:, 0] - x)**2 + (points[:, 1] - y)**2)
            nearest = np.argmin(distances)
            img_array[y, x] = colors[nearest]
    
    return Image.fromarray(img_array)


def generate_perlin_pattern(width=800, height=600, scale=100, seed=None):
    """
    Generate a pattern using simplified Perlin-like noise
    
    Args:
        width: Image width
        height: Image height
        scale: Scale of the noise pattern
        seed: Random seed
    
    Returns:
        PIL Image with noise pattern
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Create a grid of random gradients (simplified Perlin)
    grid_size = max(width, height) // scale + 2
    gradients = np.random.randn(grid_size, grid_size, 2)
    
    # Simple noise generation (not true Perlin but visually similar)
    img_array = np.zeros((height, width), dtype=np.float32)
    
    for y in range(height):
        for x in range(width):
            # Use sine waves for organic patterns
            value = 0
            value += np.sin(x / scale) * np.cos(y / scale)
            value += np.sin((x + y) / (scale * 1.5)) * 0.5
            value += np.sin((x - y) / (scale * 0.7)) * 0.3
            img_array[y, x] = value
    
    # Normalize to 0-1
    img_array = (img_array - img_array.min()) / (img_array.max() - img_array.min())
    
    # Apply color gradient
    colored = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            hue = img_array[y, x] * 0.7  # Blue-cyan range
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            colored[y, x] = [int(c * 255) for c in rgb]
    
    return Image.fromarray(colored)


if __name__ == "__main__":
    print("Algorithmic Art Generator")
    print("=" * 50)
    
    # Example: Generate Mandelbrot set
    print("Generating Mandelbrot set...")
    mandelbrot = generate_mandelbrot(800, 600, 256)
    mandelbrot.save("mandelbrot.png")
    print("Saved: mandelbrot.png")
    
    # Example: Generate Julia set
    print("Generating Julia set...")
    julia = generate_julia_set(-0.7, 0.27, 800, 600, 256)
    julia.save("julia_set.png")
    print("Saved: julia_set.png")
    
    # Example: Generate Voronoi pattern
    print("Generating Voronoi diagram...")
    voronoi = generate_voronoi_pattern(50, 800, 600, seed=42)
    voronoi.save("voronoi.png")
    print("Saved: voronoi.png")
    
    # Example: Generate Perlin-like pattern
    print("Generating Perlin-like pattern...")
    perlin = generate_perlin_pattern(800, 600, scale=80, seed=42)
    perlin.save("perlin_pattern.png")
    print("Saved: perlin_pattern.png")
    
    print("\nAll images generated successfully!")
