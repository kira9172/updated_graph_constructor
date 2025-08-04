# Planar Triangulated Graph Constructor

A sophisticated program for drawing and coloring planar triangulated graphs with dynamic vertex addition, validation, and optimization capabilities.

![Graph Constructor](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)

## Features

### Core Functionality
- **Interactive Graph Construction**: Start with a basic triangle and dynamically add vertices
- **Planar Triangulation**: Maintains proper triangulated graph structure
- **Real-time Visualization**: Live rendering with pan, zoom, and selection capabilities
- **Performance Optimized**: Handles 10,000+ vertices efficiently

### User Interface
- **Clickable Buttons**: All commands accessible via intuitive UI buttons
- **Status Display**: Real-time information about vertices, edges, and periphery
- **Mode Indicators**: Clear visual feedback for current operation mode
- **Help Text**: Hover descriptions for all buttons

### Graph Operations

#### Basic Commands
- **S - Start Triangle**: Creates initial triangle with vertices V1, V2, V3
- **R - Random Vertex**: Adds a random vertex to the graph periphery
- **A - Add Vertex**: Toggle mode to manually select two periphery vertices for new vertex placement
- **Redraw**: Optimizes vertex positions and edge lengths for better layout

#### View Controls
- **Z+ / Z-**: Zoom in/out (also available via mouse wheel)
- **C - Center**: Centers and fits the graph in the view
- **T - Toggle View**: Switch between vertex index and color display modes
- **Gm - Go to Vertex**: Show only vertices up to index m

#### Performance Features
- **Generate 1K**: Create 1000 vertices for testing
- **Generate 10K**: Create 10000 vertices for performance testing  
- **Optimize Large**: Apply optimizations for large graphs

### Advanced Features

#### Color System
- **4-Color Palette**: Natural number color system (1-4)
- **Dynamic Coloring**: Vertices automatically assigned colors based on spatial position
- **Visual Coding**: Different colors for periphery vs interior vertices

#### Graph Validation
- **Structure Validation**: Automatic checking of graph integrity
- **Error Reporting**: Clear feedback on invalid operations
- **Statistics**: Detailed graph metrics and analysis

#### Visual Enhancements
- **Curved Edges**: Smooth curved edges for better visual compaction
- **Variable Vertex Sizes**: Radius scales with vertex ID for large numbers
- **Highlighted Periphery**: Special highlighting for periphery vertices and edges
- **Selection Feedback**: Clear visual indication of selected vertices

## Usage

### Getting Started
1. Run the program: `python main.py`
2. Click "S - Start Triangle" to create the initial graph
3. Use "R - Random Vertex" or "A - Add Vertex" to expand the graph

### Manual Vertex Addition
1. Click "A - Add Vertex" to enter add vertex mode
2. Click two periphery vertices (Vp and Vq) in clockwise order
3. New vertex will be added connecting to all vertices between Vp and Vq

### Navigation
- **Mouse Wheel**: Zoom in/out
- **Left Click + Drag**: Pan the view (in graph area)
- **Right Click**: Clear selection
- **Keyboard Shortcuts**: S, R, T, C, G, A keys work as shortcuts

### Performance Testing
- Use "Generate 1K" or "Generate 10K" buttons to test with large graphs
- Apply "Optimize Large" for better performance with 10,000+ vertices
- Use "Gm" command to limit visible vertices for better performance

## Technical Implementation

### Architecture
- **Graph Class**: Manages vertices, edges, and periphery data structure
- **Vertex Class**: Handles vertex properties including position and color
- **Renderer Class**: Optimized rendering with viewport culling and curved edges
- **UI System**: Complete button-based interface with status display

### Algorithms
- **Force-Based Layout**: Physics simulation for optimal vertex positioning
- **Convex Hull Maintenance**: Ensures periphery remains convex
- **Spatial Optimization**: Performance optimizations for large graphs
- **Bezier Curves**: Smooth curved edges using quadratic bezier mathematics

### Performance Optimizations
- **Viewport Culling**: Only renders visible vertices and edges
- **Level-of-Detail**: Simplified rendering for distant objects
- **Batch Operations**: Efficient bulk vertex generation
- **Spatial Indexing**: Optimized vertex lookup and collision detection

## Requirements

- Python 3.7+
- Pygame 2.0+
- Math library (standard)
- Random library (standard)

## Installation

```bash
# Clone or download the project files
# Ensure you have pygame installed
pip install pygame

# Run the program
python main.py
```

## Graph Theory Background

This program implements **planar triangulated graphs**, where:
- All faces (except the outer face) are triangles
- The graph can be embedded in a plane without edge crossings
- The periphery forms the outer boundary of the graph
- Each new vertex maintains planarity by connecting only to periphery vertices

### Mathematical Properties
- For n vertices: approximately 3n-6 edges (Euler's formula)
- Maximum degree bounded by graph planarity
- Periphery size decreases as interior vertices are added

## Future Enhancements

- Export/Import graph data (JSON, GraphML)
- Advanced graph algorithms (shortest path, connectivity)
- Custom color palettes and themes
- Graph animation and history playback
- Multi-threading for large graph operations

## License

This project is provided as-is for educational and research purposes.

## Authors

Created as a comprehensive implementation of planar triangulated graph visualization and manipulation.
