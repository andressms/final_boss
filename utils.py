import pygame
from OpenGL.GL import *
import numpy as np
import ctypes

# --- CUBO (Paredes) ---
cube_vertices = np.array([
    -0.5, -0.5, -0.5,  0.0, 0.0,  0.0,  0.0, -1.0,
     0.5, -0.5, -0.5,  1.0, 0.0,  0.0,  0.0, -1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,  0.0,  0.0, -1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,  0.0,  0.0, -1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,  0.0,  0.0, -1.0,
    -0.5, -0.5, -0.5,  0.0, 0.0,  0.0,  0.0, -1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,  0.0,  0.0, 1.0,
     0.5, -0.5,  0.5,  1.0, 0.0,  0.0,  0.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,  0.0,  0.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,  0.0,  0.0, 1.0,
    -0.5,  0.5,  0.5,  0.0, 1.0,  0.0,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,  0.0,  0.0, 1.0,
    -0.5,  0.5,  0.5,  1.0, 0.0, -1.0,  0.0,  0.0,
    -0.5,  0.5, -0.5,  1.0, 1.0, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0, -1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0, -1.0,  0.0,  0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0, -1.0,  0.0,  0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0, -1.0,  0.0,  0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,  1.0,  0.0,  0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,  1.0,  0.0,  0.0,
     0.5, -0.5, -0.5,  0.0, 1.0,  1.0,  0.0,  0.0,
     0.5, -0.5, -0.5,  0.0, 1.0,  1.0,  0.0,  0.0,
     0.5, -0.5,  0.5,  0.0, 0.0,  1.0,  0.0,  0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,  1.0,  0.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,  0.0, -1.0,  0.0,
     0.5, -0.5, -0.5,  1.0, 1.0,  0.0, -1.0,  0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,  0.0, -1.0,  0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,  0.0, -1.0,  0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,  0.0, -1.0,  0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,  0.0, -1.0,  0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,  0.0,  1.0,  0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,  0.0,  1.0,  0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,  0.0,  1.0,  0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,  0.0,  1.0,  0.0,
    -0.5,  0.5,  0.5,  0.0, 0.0,  0.0,  1.0,  0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,  0.0,  1.0,  0.0
], dtype=np.float32)

cube_indices = np.array([i for i in range(36)], dtype=np.uint32)

# --- SPRITE (Cuadrado plano para el enemigo) ---
sprite_vertices = np.array([
    # X, Y, Z,  U, V,  Normales
    -0.5, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 
    -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 
     0.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 
     0.5, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0  
], dtype=np.float32)

sprite_indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

def create_shader(vertex_code, fragment_code):
    vertex = glCreateShader(GL_VERTEX_SHADER); glShaderSource(vertex, vertex_code); glCompileShader(vertex)
    if not glGetShaderiv(vertex, GL_COMPILE_STATUS): print(f"Vert Error: {glGetShaderInfoLog(vertex)}")
    fragment = glCreateShader(GL_FRAGMENT_SHADER); glShaderSource(fragment, fragment_code); glCompileShader(fragment)
    if not glGetShaderiv(fragment, GL_COMPILE_STATUS): print(f"Frag Error: {glGetShaderInfoLog(fragment)}")
    prog = glCreateProgram(); glAttachShader(prog, vertex); glAttachShader(prog, fragment); glLinkProgram(prog)
    return prog

def load_texture(path):
    try: 
        surface = pygame.image.load(path).convert_alpha() # IMPORTANTE: Transparencia
    except: 
        print(f"ERROR: No encontre {path}. Creando cuadro de error.")
        surface = pygame.Surface((64,64)); surface.fill((255,0,255))
    
    surface = pygame.transform.flip(surface, False, True)
    img_data = pygame.image.tostring(surface, "RGBA", 1)
    w, h = surface.get_width(), surface.get_height()
    
    tex = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    return tex

def draw_text_2d(text, x, y, font_size, window_width, window_height, color=(255, 255, 255)):
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    w, h = text_surface.get_width(), text_surface.get_height()

    glUseProgram(0) # Apagar shaders 3D
    glDisable(GL_DEPTH_TEST); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    
    tex = glGenTextures(1); glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); glOrtho(0, window_width, window_height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    
    glColor4f(1,1,1,1)
    glBegin(GL_QUADS); glTexCoord2f(0, 1); glVertex2f(x, y); glTexCoord2f(1, 1); glVertex2f(x + w, y); glTexCoord2f(1, 0); glVertex2f(x + w, y + h); glTexCoord2f(0, 0); glVertex2f(x, y + h); glEnd()
    
    glDeleteTextures([tex]); glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix()
    glDisable(GL_TEXTURE_2D); glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST)