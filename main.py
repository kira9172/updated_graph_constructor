# main.py - Enhanced Planar Graph Tool with UI Buttons
import pygame
import sys
from graph import Graph
from renderer import Renderer

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
pygame.display.set_caption("Planar Triangulated Graph Constructor")
clock = pygame.time.Clock()

# UI Constants
UI_PANEL_WIDTH = 200
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)
BUTTON_TEXT_COLOR = (255, 255, 255)
UI_BACKGROUND_COLOR = (40, 40, 60)

# --- Application State ---
graph = Graph()
renderer = Renderer(screen)
running = True
panning = False 
last_pan_pos = None

# For 'A' command: storing Vp and Vq selection
selected_vertices = [] 
visible_vertex_limit = None # For 'Gm' command
add_vertex_mode = False  # Toggle for A command mode

# UI State
font = pygame.font.SysFont('Arial', 16)
title_font = pygame.font.SysFont('Arial', 18, bold=True)
mouse_pos = (0, 0)

# Button definitions
class Button:
    def __init__(self, x, y, width, height, text, command, description=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.command = command
        self.description = description
        self.hovered = False
    
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Initialize buttons
buttons = []
y_pos = 60
button_width = UI_PANEL_WIDTH - 2 * BUTTON_MARGIN

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "S - Start Triangle", "start", "Create basic triangle V1-V2-V3"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "R - Random Vertex", "random", "Add random vertex to periphery"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "A - Add Vertex", "add_vertex", "Toggle add vertex mode"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width//2-2, BUTTON_HEIGHT, "Z+", "zoom_in", "Zoom In"))
buttons.append(Button(BUTTON_MARGIN + button_width//2+2, y_pos, button_width//2-2, BUTTON_HEIGHT, "Z-", "zoom_out", "Zoom Out"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "C - Center", "center", "Center and fit graph"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "T - Toggle View", "toggle", "Toggle index/color view"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "Toggle Curves", "toggle_curves", "Toggle curved/straight edges"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "Gm - Go to Vertex", "goto", "Show vertices up to m"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "Redraw", "redraw", "Optimize vertex positions"))
y_pos += BUTTON_HEIGHT + 15

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "Clear Selection", "clear_selection", "Clear vertex selection"))
y_pos += BUTTON_HEIGHT + 15

# Performance testing buttons
buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "Generate 1K", "generate_1k", "Generate 1000 vertices"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "Generate 10K", "generate_10k", "Generate 10000 vertices"))
y_pos += BUTTON_HEIGHT + 5

buttons.append(Button(BUTTON_MARGIN, y_pos, button_width, BUTTON_HEIGHT, "Optimize Large", "optimize", "Optimize for large graphs"))
y_pos += BUTTON_HEIGHT + 5

# UI Drawing Functions
def draw_ui():
    """Draw the user interface panel"""
    # Draw UI background
    ui_rect = pygame.Rect(0, 0, UI_PANEL_WIDTH, screen.get_height())
    pygame.draw.rect(screen, UI_BACKGROUND_COLOR, ui_rect)
    pygame.draw.line(screen, (100, 100, 100), (UI_PANEL_WIDTH, 0), (UI_PANEL_WIDTH, screen.get_height()), 2)
    
    # Draw title
    title_text = title_font.render("Graph Constructor", True, (255, 255, 255))
    screen.blit(title_text, (10, 10))
    
    # Draw buttons
    for button in buttons:
        button.draw(screen)
    
    # Draw status information
    status_y = 450
    status_texts = [
        f"Vertices: {len(graph.vertices)}",
        f"Edges: {len(graph.edges)}",
        f"Periphery: {len(graph.periphery)}",
        f"Selected: {len(selected_vertices)}",
        f"Visible: {'All' if visible_vertex_limit is None else f'≤{visible_vertex_limit}'}",
        f"Mode: {'Add Vertex' if add_vertex_mode else 'Pan/Select'}",
        f"View: {'Index' if renderer.show_index else 'Color'}",
        f"Edges: {'Curved' if renderer.use_curved_edges else 'Straight'}"
    ]
    
    for i, text in enumerate(status_texts):
        text_surface = font.render(text, True, (200, 200, 200))
        screen.blit(text_surface, (10, status_y + i * 20))
    
    # Draw instructions
    if add_vertex_mode:
        instruction_text = font.render("Click 2 periphery vertices", True, (255, 255, 100))
        screen.blit(instruction_text, (10, status_y + len(status_texts) * 20 + 20))
    
    # Draw hovered button description
    for button in buttons:
        if button.hovered and button.description:
            desc_surface = font.render(button.description, True, (200, 255, 200))
            screen.blit(desc_surface, (10, screen.get_height() - 30))
            break

def get_user_input(prompt):
    """Get user input with improved UI"""
    input_box = pygame.Rect(UI_PANEL_WIDTH + 50, 250, 300, 50)
    user_text = ''
    active = True
    
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_ESCAPE:
                    user_text = ''
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode
        
        # Draw everything
        screen.fill((20, 20, 40))
        
        # Draw graph area
        graph_surface = pygame.Surface((screen.get_width() - UI_PANEL_WIDTH, screen.get_height()))
        graph_surface.fill((20, 20, 40))
        renderer.draw_graph_on_surface(graph_surface, graph, visible_vertex_limit, selected_vertices, offset_x=0)
        screen.blit(graph_surface, (UI_PANEL_WIDTH, 0))
        
        # Draw UI
        draw_ui()
        
        # Draw input box
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (0, 0, 0), input_box, 2)
        
        prompt_surface = font.render(prompt, True, (255, 255, 255))
        screen.blit(prompt_surface, (input_box.x, input_box.y - 30))
        
        text_surface = font.render(user_text, True, (0, 0, 0))
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 15))
        
        pygame.display.flip()
    
    return user_text

def handle_button_command(command):
    """Handle button commands"""
    global add_vertex_mode, visible_vertex_limit
    
    if command == "start":
        graph.start_basic_graph()
        selected_vertices.clear()
        visible_vertex_limit = None
        add_vertex_mode = False
        renderer.reset_view(screen.get_width() - UI_PANEL_WIDTH, screen.get_height(), graph.get_bounding_box())
        
    elif command == "random":
        graph.add_random_vertex()
        
    elif command == "add_vertex":
        add_vertex_mode = not add_vertex_mode
        selected_vertices.clear()
        
    elif command == "zoom_in":
        center_pos = ((screen.get_width() - UI_PANEL_WIDTH) // 2 + UI_PANEL_WIDTH, screen.get_height() // 2)
        renderer.zoom(1.2, center_pos)
        
    elif command == "zoom_out":
        center_pos = ((screen.get_width() - UI_PANEL_WIDTH) // 2 + UI_PANEL_WIDTH, screen.get_height() // 2)
        renderer.zoom(1/1.2, center_pos)
        
    elif command == "center":
        if graph.vertices:
            renderer.reset_view(screen.get_width() - UI_PANEL_WIDTH, screen.get_height(), graph.get_bounding_box())
            
    elif command == "toggle":
        renderer.show_index = not renderer.show_index
        
    elif command == "toggle_curves":
        renderer.use_curved_edges = not renderer.use_curved_edges
        print(f"Curved edges: {'ON' if renderer.use_curved_edges else 'OFF'}")
        
    elif command == "goto":
        try:
            m_str = get_user_input("Enter vertex index 'm':")
            if m_str.strip():
                visible_vertex_limit = int(m_str)
                print(f"Showing graph up to vertex {visible_vertex_limit}")
        except (ValueError, TypeError):
            print("Invalid input. Please enter a number.")
            
    elif command == "redraw":
        graph.redraw_graph()
        
    elif command == "clear_selection":
        selected_vertices.clear()
        add_vertex_mode = False
        
    elif command == "generate_1k":
        print("Generating 1000 vertices for performance testing...")
        stats = graph.generate_large_graph(1000)
        renderer.reset_view(screen.get_width() - UI_PANEL_WIDTH, screen.get_height(), graph.get_bounding_box())
        print(f"Generated graph statistics: {stats}")
        
    elif command == "generate_10k":
        print("Generating 10000 vertices for performance testing...")
        stats = graph.generate_large_graph(10000)
        renderer.reset_view(screen.get_width() - UI_PANEL_WIDTH, screen.get_height(), graph.get_bounding_box())
        print(f"Generated graph statistics: {stats}")
        
    elif command == "optimize":
        graph.optimize_for_large_graphs()
        print("Large graph optimizations applied.")

# --- Main Loop ---
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # Update button hover states
    for button in buttons:
        button.update(mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Mouse Commands ---
        if event.type == pygame.MOUSEWHEEL:
            # Only zoom if mouse is in graph area (not UI panel)
            if mouse_pos[0] > UI_PANEL_WIDTH:
                zoom_factor = 1.1 if event.y > 0 else 1 / 1.1
                # Adjust mouse position for the graph area
                graph_mouse_pos = (mouse_pos[0] - UI_PANEL_WIDTH, mouse_pos[1])
                renderer.zoom(zoom_factor, graph_mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                # Check if clicking on UI panel
                if mouse_pos[0] < UI_PANEL_WIDTH:
                    # Handle button clicks
                    for button in buttons:
                        if button.is_clicked(mouse_pos):
                            handle_button_command(button.command)
                            break
                else:
                    # Handle graph area clicks
                    graph_mouse_pos = (mouse_pos[0] - UI_PANEL_WIDTH, mouse_pos[1])
                    clicked_vertex = renderer.get_vertex_at_pos(graph, graph_mouse_pos, visible_vertex_limit)
                    
                    if clicked_vertex and add_vertex_mode:
                        # Logic for 'A' command (Add Vertex mode)
                        if clicked_vertex.id in graph.periphery:
                            if clicked_vertex.id not in selected_vertices:
                                selected_vertices.append(clicked_vertex.id)
                                if len(selected_vertices) == 2:
                                    vp, vq = selected_vertices
                                    graph.add_vertex_to_periphery(vp, vq)
                                    selected_vertices.clear()
                                    add_vertex_mode = False
                            else:
                                selected_vertices.remove(clicked_vertex.id)
                        else:
                            print(f"Vertex {clicked_vertex.id} is not on the periphery.")
                    elif not clicked_vertex:
                        # Start panning if not clicking a vertex and not in add mode
                        panning = True
                        last_pan_pos = event.pos

            if event.button == 3: # Right mouse button - Clear selection
                selected_vertices.clear()
                add_vertex_mode = False

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Left mouse button
                panning = False
                last_pan_pos = None

        if event.type == pygame.MOUSEMOTION:
            if panning and event.pos[0] > UI_PANEL_WIDTH:
                # Pan only in graph area
                if last_pan_pos:
                    dx, dy = event.pos[0] - last_pan_pos[0], event.pos[1] - last_pan_pos[1]
                    renderer.pan_offset[0] += dx
                    renderer.pan_offset[1] += dy
                    last_pan_pos = event.pos
        
        if event.type == pygame.VIDEORESIZE:
            renderer.reset_view(event.w - UI_PANEL_WIDTH, event.h, graph.get_bounding_box())

        # --- Keyboard Commands (still supported) ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                handle_button_command("start")
            elif event.key == pygame.K_r:
                handle_button_command("random")
            elif event.key == pygame.K_t:
                handle_button_command("toggle")
            elif event.key == pygame.K_c:
                handle_button_command("center")
            elif event.key == pygame.K_g:
                handle_button_command("goto")
            elif event.key == pygame.K_a:
                handle_button_command("add_vertex")

    # --- Drawing ---
    screen.fill((15, 15, 25))  # Darker background for better contrast
    
    # Draw graph in the main area (offset by UI panel width)
    graph_surface = pygame.Surface((screen.get_width() - UI_PANEL_WIDTH, screen.get_height()))
    graph_surface.fill((25, 25, 35))  # Slightly lighter than main background
    renderer.draw_graph_on_surface(graph_surface, graph, visible_vertex_limit, selected_vertices, offset_x=0)
    screen.blit(graph_surface, (UI_PANEL_WIDTH, 0))
    
    # Draw UI panel
    draw_ui()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()