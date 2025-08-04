# renderer.py (Completed)
import pygame
import math

class Renderer:
    """Handles all drawing to the screen."""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.pan_offset = [0, 0]
        self.zoom_level = 1.0
        self.show_index = True
        self.use_curved_edges = False  # Curved edges disabled by default for cleaner appearance

    def reset_view(self, screen_w, screen_h, graph_bounds):
        if not graph_bounds or graph_bounds[2] == 0 or graph_bounds[3] == 0:
            self.pan_offset = [screen_w / 2, screen_h / 2]
            self.zoom_level = 1.0
            return

        x, y, w, h = graph_bounds
        
        # Calculate zoom to fit
        x_zoom = screen_w / w if w > 0 else 1
        y_zoom = screen_h / h if h > 0 else 1
        self.zoom_level = min(x_zoom, y_zoom) * 0.9 # 90% padding
        
        # Calculate pan to center
        graph_center_x = x + w / 2
        graph_center_y = y + h / 2
        self.pan_offset = [
            (screen_w / 2) - (graph_center_x * self.zoom_level),
            (screen_h / 2) - (graph_center_y * self.zoom_level)
        ]

    def zoom(self, factor, mouse_pos):
        # Zoom logic targeting the mouse position for a more intuitive feel
        world_pos_before_zoom = self._inverse_transform(mouse_pos)
        self.zoom_level *= factor
        world_pos_after_zoom = self._inverse_transform(mouse_pos)
        
        self.pan_offset[0] += (world_pos_after_zoom[0] - world_pos_before_zoom[0]) * self.zoom_level
        self.pan_offset[1] += (world_pos_after_zoom[1] - world_pos_before_zoom[1]) * self.zoom_level

    def draw_graph(self, graph, visible_limit=None, selected_ids=None):
        """Draws the entire graph on the main screen."""
        if selected_ids is None: selected_ids = []
        self.screen.fill((20, 20, 40)) 
        self._draw_graph_internal(self.screen, graph, visible_limit, selected_ids, 0)
        pygame.display.flip()
    
    def draw_graph_on_surface(self, surface, graph, visible_limit=None, selected_ids=None, offset_x=0):
        """Draws the graph on a given surface with offset."""
        if selected_ids is None: selected_ids = []
        self._draw_graph_internal(surface, graph, visible_limit, selected_ids, offset_x)
    
    def _draw_graph_internal(self, surface, graph, visible_limit, selected_ids, offset_x):
        """Internal method to draw graph on any surface."""
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        
        # Performance optimization: filter vertices and edges
        if visible_limit:
            visible_vertices = {k: v for k, v in graph.vertices.items() 
                              if k <= visible_limit and self._is_vertex_visible(v.pos, surface_width, surface_height)}
        else:
            # For large graphs (>1000 vertices), only render visible vertices
            if len(graph.vertices) > 1000:
                visible_vertices = {k: v for k, v in graph.vertices.items() 
                                  if self._is_vertex_visible(v.pos, surface_width, surface_height)}
            else:
                visible_vertices = graph.vertices
        
        visible_edges = {e for e in graph.edges 
                        if (e[0] in visible_vertices and e[1] in visible_vertices)}

        # Draw edges with optional curves
        for v1_id, v2_id in visible_edges:
            pos1 = self._transform_with_offset(graph.vertices[v1_id].pos, offset_x)
            pos2 = self._transform_with_offset(graph.vertices[v2_id].pos, offset_x)
            
            edge_width = max(1, int(2 * self.zoom_level))
            
            # Use curved or straight edges based on setting
            if self.use_curved_edges and self.zoom_level > 0.3:
                self._draw_smooth_curved_edge(surface, pos1, pos2, (140, 140, 160), edge_width)
            else:
                pygame.draw.line(surface, (140, 140, 160), pos1, pos2, edge_width)
        
        # Highlight periphery edges with cleaner appearance
        if len(graph.periphery) > 1:
            for i in range(len(graph.periphery)):
                v1_id = graph.periphery[i]
                v2_id = graph.periphery[(i + 1) % len(graph.periphery)]
                if (v1_id, v2_id) in visible_edges or (v2_id, v1_id) in visible_edges:
                    if v1_id in graph.vertices and v2_id in graph.vertices:
                        pos1 = self._transform_with_offset(graph.vertices[v1_id].pos, offset_x)
                        pos2 = self._transform_with_offset(graph.vertices[v2_id].pos, offset_x)
                        edge_width = max(2, int(3 * self.zoom_level))
                        pygame.draw.line(surface, (80, 200, 80), pos1, pos2, edge_width)
        
        # Draw vertices with clean, professional appearance
        for v_id, vertex in visible_vertices.items():
            pos = self._transform_with_offset(vertex.pos, offset_x)
            
            # Variable radius based on vertex ID (more conservative scaling)
            base_radius = 18 + math.log(v_id + 1, 10) * 3
            radius = int(base_radius * self.zoom_level)
            if radius < 4: continue

            # Color coding: periphery vertices are special
            is_periphery = v_id in graph.periphery
            is_selected = v_id in selected_ids
            
            # Determine colors with cleaner appearance
            if is_selected:
                outline_color = (255, 215, 0)  # Gold for selection
                outline_width = 3
            elif is_periphery:
                outline_color = (60, 180, 60)  # Darker green for periphery
                outline_width = 2
            else:
                outline_color = (200, 200, 200)  # Light gray for interior
                outline_width = 2
            
            # Draw vertex with anti-aliased circles for smoother appearance
            # Outer border
            pygame.draw.circle(surface, outline_color, pos, radius + outline_width)
            # Inner fill
            pygame.draw.circle(surface, vertex.color, pos, radius)
            # Inner highlight for 3D effect
            highlight_pos = (pos[0] - radius//3, pos[1] - radius//3)
            highlight_radius = max(2, radius//3)
            pygame.draw.circle(surface, (255, 255, 255, 100), highlight_pos, highlight_radius)

            # Draw vertex label with better contrast
            if self.show_index:
                font_size = max(10, int(14 * self.zoom_level))
                if font_size >= 8:
                    dynamic_font = pygame.font.SysFont('Arial', font_size, bold=True)
                    # Draw text with outline for better readability
                    text_surf = dynamic_font.render(str(v_id), True, (255, 255, 255))
                    text_outline = dynamic_font.render(str(v_id), True, (0, 0, 0))
                    text_rect = text_surf.get_rect(center=pos)
                    
                    # Draw outline
                    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                        outline_rect = text_rect.copy()
                        outline_rect.x += dx
                        outline_rect.y += dy
                        surface.blit(text_outline, outline_rect)
                    
                    # Draw main text
                    surface.blit(text_surf, text_rect)
    
    def get_vertex_at_pos(self, graph, screen_pos, visible_limit):
        for v_id, vertex in reversed(list(graph.vertices.items())):
            if visible_limit and v_id > visible_limit:
                continue
            
            v_screen_pos = self._transform(vertex.pos)
            radius = int((15 + math.log(v_id + 1, 10) * 5) * self.zoom_level)
            
            distance = math.sqrt((v_screen_pos[0] - screen_pos[0])**2 + (v_screen_pos[1] - screen_pos[1])**2)
            if distance <= radius:
                return vertex
        return None

    def _transform(self, pos):
        """Applies pan and zoom to a world coordinate."""
        x = pos[0] * self.zoom_level + self.pan_offset[0]
        y = pos[1] * self.zoom_level + self.pan_offset[1]
        return int(x), int(y)
    
    def _transform_with_offset(self, pos, offset_x):
        """Applies pan and zoom to a world coordinate with additional offset."""
        x = pos[0] * self.zoom_level + self.pan_offset[0] - offset_x
        y = pos[1] * self.zoom_level + self.pan_offset[1]
        return int(x), int(y)
    
    def _inverse_transform(self, screen_pos):
        """Converts a screen coordinate back to a world coordinate."""
        x = (screen_pos[0] - self.pan_offset[0]) / self.zoom_level
        y = (screen_pos[1] - self.pan_offset[1]) / self.zoom_level
        return x, y
    
    def _draw_smooth_curved_edge(self, surface, pos1, pos2, color, width):
        """Draw a smooth curved edge between two points."""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 10:  # Too short for curves
            pygame.draw.line(surface, color, pos1, pos2, width)
            return
        
        # Create a gentle curve with much smaller curvature
        mid_x = (pos1[0] + pos2[0]) / 2
        mid_y = (pos1[1] + pos2[1]) / 2
        
        # Very subtle curve - only 5% of edge length
        curve_factor = min(10, length * 0.05)
        perp_x = -dy / length * curve_factor
        perp_y = dx / length * curve_factor
        
        control_x = int(mid_x + perp_x)
        control_y = int(mid_y + perp_y)
        
        # Draw smooth curve with fewer, cleaner segments
        points = []
        num_segments = max(4, min(12, int(length / 30)))
        
        for i in range(num_segments + 1):
            t = i / num_segments
            # Quadratic bezier curve
            x = (1-t)**2 * pos1[0] + 2*(1-t)*t * control_x + t**2 * pos2[0]
            y = (1-t)**2 * pos1[1] + 2*(1-t)*t * control_y + t**2 * pos2[1]
            points.append((int(x), int(y)))
        
        # Draw smooth connected segments
        try:
            for i in range(len(points) - 1):
                pygame.draw.line(surface, color, points[i], points[i+1], width)
        except (ValueError, OverflowError):
            # Fallback to straight line
            pygame.draw.line(surface, color, pos1, pos2, width)
    
    def _is_vertex_visible(self, vertex_pos, screen_width, screen_height):
        """Check if a vertex is visible on screen for performance optimization."""
        screen_pos = self._transform_with_offset(vertex_pos, 0)
        margin = 100  # Extra margin for partially visible vertices
        return (-margin <= screen_pos[0] <= screen_width + margin and 
                -margin <= screen_pos[1] <= screen_height + margin)