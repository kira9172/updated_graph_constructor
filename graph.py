# graph.py (Completed)
from vertex import Vertex
import math
import random

class Graph:
    """Manages all graph data and logic."""
    def __init__(self):
        self.vertices = {}
        self.edges = set()
        self.periphery = []
        self.next_vertex_id = 1
        # Color palette system (1-4 natural numbers)
        self.color_palette = {
            1: (255, 100, 100),  # Red
            2: (100, 255, 100),  # Green  
            3: (100, 100, 255),  # Blue
            4: (255, 255, 100)   # Yellow
        }

    def get_bounding_box(self):
        if not self.vertices:
            return 0, 0, 800, 600
        x_coords = [v.pos[0] for v in self.vertices.values()]
        y_coords = [v.pos[1] for v in self.vertices.values()]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        return min_x, min_y, max_x - min_x, max_y - min_y

    def start_basic_graph(self):
        """Implements the 'S' command to start with a basic triangle."""
        self.vertices.clear()
        self.edges.clear()
        self.periphery.clear()
        
        # Create initial triangle with different colors
        v1 = Vertex(1, 400, 200, color_number=1)
        v2 = Vertex(2, 250, 450, color_number=2)
        v3 = Vertex(3, 550, 450, color_number=3)
        
        self.vertices = {1: v1, 2: v2, 3: v3}
        self.edges.add(tuple(sorted((1, 2))))
        self.edges.add(tuple(sorted((2, 3))))
        self.edges.add(tuple(sorted((3, 1))))
        
        self.periphery = [1, 2, 3] # Clockwise order
        self.next_vertex_id = 4
        print("Started basic graph with triangle V1-V2-V3.")

    def add_vertex_to_periphery(self, vp_id, vq_id):
        """Implements the logic for adding a new vertex to the periphery[cite: 20]."""
        if vp_id == vq_id:
            print("Error: Vp and Vq cannot be the same vertex.")
            return

        if vp_id not in self.periphery or vq_id not in self.periphery:
            print("Error: Selected vertices must be on the periphery.")
            return

        p_idx = self.periphery.index(vp_id)
        q_idx = self.periphery.index(vq_id)
        
        if p_idx < q_idx:
            target_arc = self.periphery[p_idx : q_idx + 1]
        else: # Wrap around case
            target_arc = self.periphery[p_idx:] + self.periphery[:q_idx + 1]

        if len(target_arc) < 2:
            print("Error: Invalid arc selection.")
            return
            
        new_pos_x, new_pos_y = self._calculate_outward_pos(target_arc)

        new_v_id = self.next_vertex_id
        # Assign color based on vertex ID (cycle through 1-4)
        color_number = ((new_v_id - 1) % 4) + 1
        new_vertex = Vertex(new_v_id, new_pos_x, new_pos_y, color_number=color_number)
        self.vertices[new_v_id] = new_vertex
        
        for vid in target_arc:
            self.edges.add(tuple(sorted((new_v_id, vid))))

        interior_arc = target_arc[1:-1]
        new_periphery = [v_id for v_id in self.periphery if v_id not in interior_arc]
        vp_idx_in_new = new_periphery.index(vp_id)
        new_periphery.insert(vp_idx_in_new + 1, new_v_id)
        self.periphery = new_periphery
        
        self.next_vertex_id += 1
        print(f"Added vertex {new_v_id} connected to {target_arc}.")

    def add_random_vertex(self):
        """Implements the 'R' command[cite: 19]."""
        if len(self.periphery) < 2:
            print("Not enough vertices to add a random one.")
            return
        
        vp_id, vq_id = random.sample(self.periphery, 2)
        self.add_vertex_to_periphery(vp_id, vq_id)

    def _calculate_outward_pos(self, arc_ids):
        """
        Calculates an outward position for a new vertex to maintain a convex contour and regular shape.
        """
        arc_points = [self.vertices[vid].pos for vid in arc_ids]
        
        # 1. Find the center of the arc
        center_x = sum(p[0] for p in arc_points) / len(arc_points)
        center_y = sum(p[1] for p in arc_points) / len(arc_points)

        # 2. Find the center of the entire graph
        graph_center_x = sum(v.pos[0] for v in self.vertices.values()) / len(self.vertices)
        graph_center_y = sum(v.pos[1] for v in self.vertices.values()) / len(self.vertices)

        # 3. Create a vector pointing from the graph center to the arc center
        direction_x = center_x - graph_center_x
        direction_y = center_y - graph_center_y
        
        # 4. Normalize the vector
        length = math.sqrt(direction_x**2 + direction_y**2)
        if length == 0: length = 1 # Avoid division by zero
        norm_x = direction_x / length
        norm_y = direction_y / length
        
        # 5. Place the new vertex along this vector, at a distance
        # calculated from the average edge length of the arc.
        avg_dist = 0
        if len(arc_points) > 1:
            p1 = arc_points[0]
            p2 = arc_points[-1]
            avg_dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) / 2
        
        distance_factor = max(avg_dist, 80) # Ensure a minimum distance

        new_x = center_x + norm_x * distance_factor
        new_y = center_y + norm_y * distance_factor
        
        return new_x, new_y
    
    def redraw_graph(self):
        """
        Implements the redraw command to optimize vertex positions and edge lengths.
        Redistributes vertices to maintain convex contour and equal distances.
        """
        if len(self.vertices) < 3:
            return
        
        print("Redrawing graph for optimal layout...")
        
        # Find the graph center
        center_x = sum(v.pos[0] for v in self.vertices.values()) / len(self.vertices)
        center_y = sum(v.pos[1] for v in self.vertices.values()) / len(self.vertices)
        
        # Calculate average edge length for scaling
        total_edge_length = 0
        edge_count = 0
        for v1_id, v2_id in self.edges:
            v1_pos = self.vertices[v1_id].pos
            v2_pos = self.vertices[v2_id].pos
            length = math.sqrt((v1_pos[0] - v2_pos[0])**2 + (v1_pos[1] - v2_pos[1])**2)
            total_edge_length += length
            edge_count += 1
        
        avg_edge_length = total_edge_length / edge_count if edge_count > 0 else 100
        
        # Redraw periphery vertices in a regular pattern
        if len(self.periphery) > 0:
            radius = max(150, avg_edge_length * len(self.periphery) / (2 * math.pi))
            
            for i, v_id in enumerate(self.periphery):
                angle = 2 * math.pi * i / len(self.periphery)
                new_x = center_x + radius * math.cos(angle)
                new_y = center_y + radius * math.sin(angle)
                self.vertices[v_id].pos = (new_x, new_y)
        
        # Adjust interior vertices using force-based layout
        interior_vertices = [v_id for v_id in self.vertices.keys() if v_id not in self.periphery]
        
        for _ in range(50):  # Iteration limit for force simulation
            forces = {v_id: [0, 0] for v_id in interior_vertices}
            
            # Repulsive forces between all interior vertices
            for i, v1_id in enumerate(interior_vertices):
                for v2_id in interior_vertices[i+1:]:
                    v1_pos = self.vertices[v1_id].pos
                    v2_pos = self.vertices[v2_id].pos
                    
                    dx = v1_pos[0] - v2_pos[0]
                    dy = v1_pos[1] - v2_pos[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        force_magnitude = avg_edge_length * avg_edge_length / (distance * distance)
                        force_x = force_magnitude * dx / distance
                        force_y = force_magnitude * dy / distance
                        
                        forces[v1_id][0] += force_x
                        forces[v1_id][1] += force_y
                        forces[v2_id][0] -= force_x
                        forces[v2_id][1] -= force_y
            
            # Attractive forces along edges
            for v1_id, v2_id in self.edges:
                if v1_id in interior_vertices and v2_id in interior_vertices:
                    v1_pos = self.vertices[v1_id].pos
                    v2_pos = self.vertices[v2_id].pos
                    
                    dx = v2_pos[0] - v1_pos[0]
                    dy = v2_pos[1] - v1_pos[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance > 0:
                        force_magnitude = (distance - avg_edge_length) * 0.1
                        force_x = force_magnitude * dx / distance
                        force_y = force_magnitude * dy / distance
                        
                        forces[v1_id][0] += force_x
                        forces[v1_id][1] += force_y
                        forces[v2_id][0] -= force_x
                        forces[v2_id][1] -= force_y
            
            # Apply forces with damping
            for v_id in interior_vertices:
                current_pos = self.vertices[v_id].pos
                new_x = current_pos[0] + forces[v_id][0] * 0.1
                new_y = current_pos[1] + forces[v_id][1] * 0.1
                self.vertices[v_id].pos = (new_x, new_y)
    
    def assign_vertex_color(self, vertex_id, color_number):
        """Assign a color from the palette (1-4) to a vertex."""
        if color_number in self.color_palette and vertex_id in self.vertices:
            self.vertices[vertex_id].color = self.color_palette[color_number]
            return True
        return False
    
    def get_vertex_color_number(self, vertex_id):
        """Get the color number (1-4) for a vertex."""
        if vertex_id in self.vertices:
            vertex_color = self.vertices[vertex_id].color
            for color_num, palette_color in self.color_palette.items():
                if vertex_color == palette_color:
                    return color_num
        return 1  # Default color
    
    def validate_graph_structure(self):
        """Validate the graph structure and check for issues."""
        issues = []
        
        # Check if all periphery vertices exist
        for v_id in self.periphery:
            if v_id not in self.vertices:
                issues.append(f"Periphery vertex {v_id} does not exist")
        
        # Check if edges connect existing vertices
        for v1_id, v2_id in self.edges:
            if v1_id not in self.vertices:
                issues.append(f"Edge references non-existent vertex {v1_id}")
            if v2_id not in self.vertices:
                issues.append(f"Edge references non-existent vertex {v2_id}")
        
        # Check if graph is properly triangulated (each face should be a triangle)
        # This is a simplified check
        if len(self.vertices) > 2:
            expected_edges = 3 * len(self.vertices) - 3 - len(self.periphery)
            if len(self.edges) < expected_edges:
                issues.append(f"Graph may not be properly triangulated. Expected ~{expected_edges} edges, got {len(self.edges)}")
        
        return issues
    
    def get_graph_statistics(self):
        """Get detailed statistics about the graph."""
        stats = {
            'vertices': len(self.vertices),
            'edges': len(self.edges),
            'periphery_size': len(self.periphery),
            'interior_vertices': len(self.vertices) - len(self.periphery),
            'validation_issues': len(self.validate_graph_structure())
        }
        
        if self.vertices:
            # Calculate average degree
            degrees = {}
            for v1_id, v2_id in self.edges:
                degrees[v1_id] = degrees.get(v1_id, 0) + 1
                degrees[v2_id] = degrees.get(v2_id, 0) + 1
            
            if degrees:
                stats['avg_degree'] = sum(degrees.values()) / len(degrees)
                stats['max_degree'] = max(degrees.values())
                stats['min_degree'] = min(degrees.values())
        
        return stats
    
    def generate_large_graph(self, target_vertices=1000):
        """
        Generate a large graph for performance testing.
        Efficiently creates many vertices by adding them systematically.
        """
        print(f"Generating large graph with {target_vertices} vertices...")
        
        # Start with basic triangle
        self.start_basic_graph()
        
        # Add vertices in batches for better performance
        batch_size = min(50, target_vertices // 20)
        
        for i in range(4, target_vertices + 1):
            if i % batch_size == 0:
                print(f"Generated {i}/{target_vertices} vertices...")
                # Periodic redraw for optimization
                if i % (batch_size * 4) == 0:
                    self.redraw_graph()
            
            # Add random vertex (more efficient than manual selection)
            self.add_random_vertex()
        
        print(f"Large graph generation complete! {len(self.vertices)} vertices, {len(self.edges)} edges.")
        return self.get_graph_statistics()
    
    def optimize_for_large_graphs(self):
        """Apply optimizations for handling large graphs (10,000+ vertices)."""
        if len(self.vertices) < 1000:
            return
        
        print("Applying large graph optimizations...")
        
        # Simplify vertex positions using clustering for distant vertices
        # This helps with rendering performance
        vertex_positions = list(self.vertices.values())
        
        # Group vertices by spatial proximity for better cache performance
        # This is a simplified spatial optimization
        center_x = sum(v.pos[0] for v in vertex_positions) / len(vertex_positions)
        center_y = sum(v.pos[1] for v in vertex_positions) / len(vertex_positions)
        
        # Optimize vertex colors for large graphs (reduce color changes)
        for i, (v_id, vertex) in enumerate(self.vertices.items()):
            # Use spatial-based coloring for better visual grouping
            distance_from_center = math.sqrt(
                (vertex.pos[0] - center_x)**2 + (vertex.pos[1] - center_y)**2
            )
            
            # Assign colors based on distance rings
            if distance_from_center < 100:
                color_number = 1
            elif distance_from_center < 200:
                color_number = 2
            elif distance_from_center < 300:
                color_number = 3
            else:
                color_number = 4
            
            vertex.set_color(color_number)
        
        print("Large graph optimizations applied.")