# vertex.py

class Vertex:
    """A vertex in the planar triangulated graph."""
    def __init__(self, id, pos_x, pos_y, color_number=1):
        # Every vertex has an associated location (X, Y) in the plane
        self.id = id
        self.pos = (pos_x, pos_y)
        
        # Color system: vertices are represented by circles with configurable colors
        # Default color palette (can be modified by the graph)
        self.color_palette = {
            1: (255, 120, 120),  # Light Red
            2: (120, 255, 120),  # Light Green  
            3: (120, 120, 255),  # Light Blue
            4: (255, 255, 120)   # Light Yellow
        }
        
        # Set initial color based on color number (1-4)
        self.color_number = max(1, min(4, color_number))
        self.color = self.color_palette[self.color_number]
        
        # Variable radius based on vertex ID for better visibility of large numbers
        self.base_radius = 15
        self.radius = self.calculate_radius()
    
    def calculate_radius(self):
        """Calculate appropriate radius based on vertex ID."""
        import math
        # Increase radius logarithmically with vertex ID
        return self.base_radius + math.log(self.id + 1, 10) * 5
    
    def set_color(self, color_number):
        """Set vertex color using color number (1-4)."""
        if 1 <= color_number <= 4:
            self.color_number = color_number
            self.color = self.color_palette[color_number]
            return True
        return False
    
    def set_custom_color(self, rgb_color):
        """Set a custom RGB color for the vertex."""
        if isinstance(rgb_color, tuple) and len(rgb_color) == 3:
            self.color = rgb_color
            # Try to find matching color number, or default to 1
            for num, palette_color in self.color_palette.items():
                if palette_color == rgb_color:
                    self.color_number = num
                    return
            self.color_number = 1
    
    def get_display_info(self):
        """Get information for display purposes."""
        return {
            'id': self.id,
            'position': self.pos,
            'color': self.color,
            'color_number': self.color_number,
            'radius': self.radius
        }