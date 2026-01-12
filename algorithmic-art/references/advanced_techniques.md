# Advanced Algorithmic Art Techniques

This document provides detailed information on advanced generative art algorithms and computational creativity techniques.

## L-Systems (Lindenmayer Systems)

L-systems are parallel rewriting systems used to model plant growth and create fractal patterns.

### Basic L-System Structure
- **Axiom**: Starting string (e.g., "F")
- **Rules**: Replacement rules (e.g., F → F+F--F+F)
- **Angle**: Rotation angle for turtle graphics
- **Iterations**: Number of times to apply rules

### Common L-System Patterns

**Koch Curve**:
- Axiom: F
- Rule: F → F+F--F+F
- Angle: 60°

**Dragon Curve**:
- Axiom: FX
- Rules: X → X+YF+, Y → -FX-Y
- Angle: 90°

**Fractal Plant**:
- Axiom: X
- Rules: X → F+[[X]-X]-F[-FX]+X, F → FF
- Angle: 25°

### Implementation Tips
- Use turtle graphics for rendering
- Stack-based approach for branching ([, ])
- Parametric L-systems allow varying parameters

## Reaction-Diffusion Systems

Simulate chemical reactions that create organic patterns (Turing patterns).

### Gray-Scott Model
```
∂u/∂t = Du∇²u - uv² + F(1-u)
∂v/∂t = Dv∇²v + uv² - (F+k)v
```

Parameters:
- Du, Dv: Diffusion rates
- F: Feed rate
- k: Kill rate

### Pattern Types (F, k values)
- **Spots**: F=0.035, k=0.060
- **Stripes**: F=0.035, k=0.065
- **Spirals**: F=0.030, k=0.062
- **Waves**: F=0.025, k=0.060

## Strange Attractors

Chaotic systems that create beautiful patterns.

### Lorenz Attractor
```
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y
dz/dt = xy - βz
```

Classic parameters: σ=10, ρ=28, β=8/3

### Rössler Attractor
```
dx/dt = -y - z
dy/dt = x + ay
dz/dt = b + z(x - c)
```

Parameters: a=0.2, b=0.2, c=5.7

### De Jong Attractor
```
x_new = sin(a*y) - cos(b*x)
y_new = sin(c*x) - cos(d*y)
```

Experiment with a, b, c, d in range [-3, 3]

## Cellular Automata

### Conway's Game of Life
Rules:
- Birth: Dead cell with exactly 3 neighbors becomes alive
- Survival: Live cell with 2-3 neighbors survives
- Death: All other cells die

### Elementary Cellular Automata
- 1D grid, 8 possible neighborhoods
- 256 possible rules (Rule 30, Rule 110, etc.)
- Rule 30: Chaotic, used in Mathematica's random number generator

### 2D Cellular Automata Variations
- **Brian's Brain**: 3 states (firing, refractory, off)
- **Langton's Ant**: Simple rules, complex emergent behavior
- **Cyclic Cellular Automaton**: Colors cycle through states

## Particle Systems

### Boids Algorithm (Flocking)
Three simple rules create complex flocking behavior:
1. **Separation**: Steer to avoid crowding neighbors
2. **Alignment**: Steer towards average heading of neighbors
3. **Cohesion**: Steer towards average position of neighbors

### Flow Fields
- Use Perlin noise to create smooth vector field
- Particles follow field direction
- Add curl noise for swirling effects

### Diffusion-Limited Aggregation (DLA)
- Random walkers stick to a growing structure
- Creates branching, tree-like patterns
- Similar to crystal growth, lightning, coral

## Noise Functions

### Perlin Noise
- Gradient noise with smooth interpolation
- Natural-looking randomness
- Scales well (octaves for detail)

### Simplex Noise
- Ken Perlin's improved algorithm
- Better performance in higher dimensions
- No directional artifacts

### Worley Noise (Cellular Noise)
- Based on distance to random points
- Creates cell-like patterns
- Useful for textures (stone, water, clouds)

## Fourier Art

### Epicycles
- Sum of rotating circles (Fourier series)
- Can draw any closed path
- Beautiful animated visualizations

### Fourier Transform Visualization
- Convert images to frequency domain
- Manipulate frequencies
- Inverse transform for artistic effects

## Tessellations and Tilings

### Penrose Tiling
- Aperiodic tiling with fivefold symmetry
- Two rhombi shapes
- Golden ratio proportions

### Voronoi Diagrams
- Partition space by nearest point
- Creates cellular patterns
- Useful for organic textures

### Delaunay Triangulation
- Dual of Voronoi diagram
- Maximum angle triangulation
- Creates geometric mesh patterns

## Recursive Algorithms

### Sierpinski Triangle
- Remove central triangle recursively
- Creates fractal structure
- Can be colored by iteration depth

### Tree Fractals
- Recursive branching
- Vary angle, length ratio, randomness
- Natural-looking trees

### Maze Generation
- Recursive backtracking
- Creates perfect mazes
- Visually interesting patterns

## Physics Simulations

### Double Pendulum
- Chaotic motion
- Trace path for artistic patterns
- Sensitivity to initial conditions

### N-Body Simulation
- Gravitational interactions
- Creates swirling, galaxy-like patterns
- Barnes-Hut algorithm for optimization

### Cloth Simulation
- Mass-spring systems
- Creates flowing, organic shapes
- Wind forces for variety

## Advanced Color Techniques

### Color Harmony
- Complementary: Opposite on color wheel
- Analogous: Adjacent colors
- Triadic: Evenly spaced (120°)
- Tetradic: Two complementary pairs

### Gradient Mapping
- Map values to color gradients
- Smooth transitions
- Custom palette definition

### Palette Generation
- Extract from images
- Golden ratio color spacing
- Perceptually uniform color spaces (LAB, LCH)

## Optimization Tips

### Performance
- Use NumPy for vectorized operations
- Numba JIT compilation for Python
- GPU acceleration (OpenGL, CUDA, WebGL)
- Multiprocessing for batch generation

### Quality
- Supersampling (render at 2x-4x, downsample)
- Anti-aliasing
- Dithering for color reduction
- Post-processing filters

## Mathematical Formulas for Art

### Parametric Curves
- **Lissajous**: x=A·sin(at+δ), y=B·sin(bt)
- **Spirograph**: x=R[(1-k)cos(t)+l·k·cos((1-k)t/k)]
- **Rose Curves**: r=cos(k·θ)

### Polar Equations
- **Cardioid**: r=a(1+cos(θ))
- **Logarithmic Spiral**: r=ae^(bθ)
- **Archimedes Spiral**: r=aθ

### 3D Surfaces
- **Torus**: Parametric surface, donut shape
- **Möbius Strip**: Non-orientable surface
- **Klein Bottle**: 4D object projected to 3D

## Randomness and Seeds

### Controlled Randomness
- Always use seeds for reproducibility
- Save seed with artwork metadata
- Multiple RNG streams for different elements

### Noise Sources
- True random: /dev/urandom, random.org
- Pseudo-random: Mersenne Twister, PCG
- Deterministic: Hash functions, LCG

### Constrained Randomness
- Gaussian distribution for natural variance
- Rejection sampling for specific ranges
- Weighted random choices

## Export Considerations

### Vector vs Raster
- **Vector (SVG)**: Scalable, small file size, limited effects
- **Raster (PNG)**: Full color, effects, fixed resolution

### Resolution Guidelines
- Web display: 72-96 DPI
- Print quality: 300 DPI minimum
- Large format: 150 DPI acceptable
- Calculate dimensions: pixels = inches × DPI

### File Formats
- **PNG**: Lossless, transparency support
- **SVG**: Vector, scalable, web-friendly
- **PDF**: Print-ready, can embed vectors
- **GIF**: Animation, limited colors
- **MP4**: Video export for animations

## Inspiration and References

### Artists
- **Manfred Mohr**: Pioneer of algorithmic art
- **Vera Molnár**: Early computer art, geometric abstraction
- **Frieder Nake**: Mathematical art
- **Georg Nees**: Generative graphics
- **Casey Reas**: Processing co-creator
- **Tyler Hobbs**: Fidenza, Flow Fields

### Resources
- **Processing**: Creative coding framework
- **p5.js**: JavaScript version of Processing
- **OpenFrameworks**: C++ creative coding
- **Shadertoy**: GPU shader art community
- **generativehut.com**: Tutorials and inspiration

### Books
- "The Nature of Code" - Daniel Shiffman
- "Generative Art" - Matt Pearson  
- "Algorithmic Beauty of Plants" - Prusinkiewicz
- "Form+Code" - Casey Reas and Chandler McWilliams

## Combining Techniques

The most interesting algorithmic art often combines multiple techniques:

- L-systems + Perlin noise → Organic plant growth
- Voronoi + Gradient mapping → Stained glass effect
- Particles + Strange attractors → Chaotic flows
- Cellular automata + Color cycling → Dynamic patterns
- Fractals + Symmetry → Kaleidoscopic effects

Experiment, iterate, and explore! Algorithmic art is about discovering emergent beauty in mathematical systems.
