import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from pyrr import matrix44, Vector3
import math
import os
import config, shaders, camera, utils

# --- CLASE ENEMIGO ---
class Enemigo:
    def __init__(self, x, z):
        self.pos = np.array([float(x), 0.0, float(z)], dtype=np.float32)
        self.velocidad = config.VELOCIDAD_ENEMIGO
        self.radio = 0.2 

    def puede_moverse(self, x, z, mapa):
        gx, gz = int(x), int(z)
        if 0 <= gz < len(mapa) and 0 <= gx < len(mapa[0]):
            return mapa[gz][gx] != 1
        return False

    def mover(self, target, mapa):
        dir_vector = target - self.pos; dir_vector[1] = 0 
        distancia = np.linalg.norm(dir_vector)

        if distancia > 0.1: 
            dir_vector /= distancia 
            move_step = dir_vector * self.velocidad
            next_pos = self.pos + move_step
            
            if self.puede_moverse(next_pos[0], next_pos[2], mapa):
                self.pos = next_pos
            else:
                next_pos_x = self.pos + np.array([move_step[0], 0, 0])
                if self.puede_moverse(next_pos_x[0], next_pos_x[2], mapa): self.pos = next_pos_x
                else:
                    next_pos_z = self.pos + np.array([0, 0, move_step[2]])
                    if self.puede_moverse(next_pos_z[0], next_pos_z[2], mapa): self.pos = next_pos_z

def main():
    pygame.init()
    # INICIAR AUDIO
    pygame.mixer.init()

    pygame.display.set_mode((config.ANCHO, config.ALTO), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("LABERINTO TERROR")
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.02, 0.02, 0.05, 1.0) 

    shader = utils.create_shader(shaders.vertex_shader, shaders.fragment_shader)
    
    # BUFFERS
    VAO_cube = glGenVertexArrays(1); glBindVertexArray(VAO_cube)
    VBO_cube = glGenBuffers(1); glBindBuffer(GL_ARRAY_BUFFER, VBO_cube); glBufferData(GL_ARRAY_BUFFER, utils.cube_vertices.nbytes, utils.cube_vertices, GL_STATIC_DRAW)
    EBO_cube = glGenBuffers(1); glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_cube); glBufferData(GL_ELEMENT_ARRAY_BUFFER, utils.cube_indices.nbytes, utils.cube_indices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0)); glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12)); glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20)); glEnableVertexAttribArray(2)

    VAO_sprite = glGenVertexArrays(1); glBindVertexArray(VAO_sprite)
    VBO_sprite = glGenBuffers(1); glBindBuffer(GL_ARRAY_BUFFER, VBO_sprite); glBufferData(GL_ARRAY_BUFFER, utils.sprite_vertices.nbytes, utils.sprite_vertices, GL_STATIC_DRAW)
    EBO_sprite = glGenBuffers(1); glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO_sprite); glBufferData(GL_ELEMENT_ARRAY_BUFFER, utils.sprite_indices.nbytes, utils.sprite_indices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0)); glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12)); glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20)); glEnableVertexAttribArray(2)

    # TEXTURAS
    base_path = os.path.dirname(os.path.abspath(__file__))
    tex_wall = utils.load_texture(os.path.join(base_path, "wall.jpg"))
    ruta_enemigo = os.path.join(base_path, "final_boss", "enemy.jpg")
    try: tex_enemy = utils.load_texture(ruta_enemigo)
    except: tex_enemy = 0

    # --- CARGAR MUSICA MP3 ---
    # Busca en carpeta final_boss primero
    ruta_musica = os.path.join(base_path, "final_boss", "musica.mp3")
    
    # Si no esta, busca en la raiz
    if not os.path.exists(ruta_musica):
        ruta_musica = os.path.join(base_path, "musica.mp3")

    try:
        pygame.mixer.music.load(ruta_musica)
        pygame.mixer.music.set_volume(0.4) 
        pygame.mixer.music.play(-1) # Loop infinito
        print(f"Reproduciendo: {ruta_musica}")
    except Exception as e:
        print(f"Error de audio (¿Esta el archivo musica.mp3?): {e}")

    cam = camera.Camera()
    clock = pygame.time.Clock()
    
    estado = 0; nivel_idx = 0; enemigo = None; flash = 0.0; rotation_time = 0.0
    tiempo_inmunidad = 0.0 

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        rotation_time += dt
        if tiempo_inmunidad > 0: tiempo_inmunidad -= dt
        
        mouse_mov = (0,0)
        
        # EVENTOS (Solo clicks y cerrar)
        for event in pygame.event.get():
            if event.type == QUIT: running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if estado == 1: estado = 0
                    else: running = False
                if event.key == K_RETURN:
                    if estado == 0: 
                        estado = 1; pygame.mouse.set_visible(False); pygame.event.set_grab(True)
                        cam.pos = np.array([1.5, 1.5, 1.5], dtype=np.float32)
                        mapa_actual = config.MAPAS[nivel_idx]
                        enemigo = Enemigo(len(mapa_actual[0]) - 2.5, len(mapa_actual) - 2.5)
                        cam.vidas = 3 
                    if estado >= 2: 
                        estado = 0; nivel_idx = 0; cam.vidas = 3

            if event.type == MOUSEMOTION and estado == 1: mouse_mov = event.rel

        # MOVIMIENTO FLUIDO (W,A,S,D sin pausas)
        keys = pygame.key.get_pressed()

        if estado == 1:
            cam.input(keys, mouse_mov, config.MAPAS[nivel_idx])
            res = cam.update_physics(config.MAPAS[nivel_idx])
            
            if res == "PINCHO" and tiempo_inmunidad <= 0:
                cam.vidas-=1; flash=1.0; tiempo_inmunidad = 1.0
            
            if enemigo:
                enemigo.mover(cam.pos, config.MAPAS[nivel_idx])
                dist = np.sqrt((cam.pos[0]-enemigo.pos[0])**2 + (cam.pos[2]-enemigo.pos[2])**2)
                
                # HITBOX 0.25 Y COOLDOWN
                if dist < 0.25 and tiempo_inmunidad <= 0:
                    cam.vidas -= 1; flash = 1.0; tiempo_inmunidad = 2.0 
                    direccion = cam.pos - enemigo.pos
                    cam.pos += direccion * 1.5
                    print(f"GOLPE! Vidas: {cam.vidas}")

            if cam.vidas <= 0: estado = 2; pygame.mouse.set_visible(True); pygame.event.set_grab(False)

            gx, gz = int(cam.pos[0]), int(cam.pos[2])
            if config.MAPAS[nivel_idx][gz][gx] == 3:
                nivel_idx += 1
                if nivel_idx >= len(config.MAPAS): estado=3; pygame.mouse.set_visible(True); pygame.event.set_grab(False)
                else: 
                    cam.pos = np.array([1.5, 1.5, 1.5], dtype=np.float32)
                    mapa_actual = config.MAPAS[nivel_idx]
                    enemigo = Enemigo(len(mapa_actual[0])-2.5, len(mapa_actual)-2.5)

        # RENDER
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)

        if estado == 1: view = cam.get_view_matrix()
        else: 
            cam_x = 7.5 + np.sin(rotation_time)*10
            cam_z = 7.5 + np.cos(rotation_time)*10
            view = matrix44.create_look_at(Vector3([cam_x, 8, cam_z]), Vector3([7.5, 0, 7.5]), Vector3([0,1,0]))

        proj = matrix44.create_perspective_projection_matrix(50, config.ANCHO/config.ALTO, 0.1, 100)
        
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, proj)
        glUniform3fv(glGetUniformLocation(shader, "lightPos"), 1, cam.pos)
        glUniform1f(glGetUniformLocation(shader, "damageFlash"), flash)
        if flash > 0: flash -= 0.05

        glBindVertexArray(VAO_cube)
        glBindTexture(GL_TEXTURE_2D, tex_wall)
        mapa = config.MAPAS[nivel_idx]
        for r, row in enumerate(mapa):
            for c, tile in enumerate(row):
                model = matrix44.create_from_translation(Vector3([c, 0, r]))
                glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
                glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, config.COLOR_SUELO)
                glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
                
                if tile == 1:
                    # PAREDES ALTAS
                    model = matrix44.create_from_scale(Vector3([1.0, 6.0, 1.0]))
                    model = matrix44.multiply(model, matrix44.create_from_translation(Vector3([c, 0, r])))
                    glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
                    glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, config.COLOR_PARED)
                    glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)
                elif tile == 3:
                    rot = matrix44.create_from_y_rotation(rotation_time * 3)
                    scale = matrix44.create_from_scale(Vector3([0.6, 0.6, 0.6]))
                    trans = matrix44.create_from_translation(Vector3([c, 0.5 + np.sin(rotation_time)*0.2, r]))
                    model = matrix44.multiply(scale, rot); model = matrix44.multiply(model, trans)
                    glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
                    glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, (0.2, 1.0, 0.2))
                    glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        if enemigo:
            glBindVertexArray(VAO_sprite)
            glBindTexture(GL_TEXTURE_2D, tex_enemy)
            delta_x = cam.pos[0] - enemigo.pos[0]; delta_z = cam.pos[2] - enemigo.pos[2]
            angle = -math.atan2(delta_z, delta_x) + math.pi/2
            
            scale = matrix44.create_from_scale(Vector3([0.8, 1.5, 1.0]))
            rot = matrix44.create_from_y_rotation(angle)
            trans = matrix44.create_from_translation(enemigo.pos)
            model = matrix44.multiply(scale, rot); model = matrix44.multiply(model, trans)
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
            
            color = (1,1,1) if tiempo_inmunidad <= 0 else (1, 0, 0)
            glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, color)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        glUseProgram(0) 
        if estado == 0:
            utils.draw_text_2d("LABERINTO TERROR", config.ANCHO//2 - 250, 150, 60, config.ANCHO, config.ALTO, (200, 0, 0))
            utils.draw_text_2d("[ENTER] JUGAR", config.ANCHO//2 - 120, 300, 30, config.ANCHO, config.ALTO)
        elif estado == 1:
            utils.draw_text_2d("♥ " * cam.vidas, 20, 20, 50, config.ANCHO, config.ALTO, (255, 0, 0))
            if tiempo_inmunidad > 0:
                 utils.draw_text_2d("¡HUYE!", config.ANCHO//2 - 50, config.ALTO//2, 40, config.ANCHO, config.ALTO, (255, 255, 0))
            utils.draw_text_2d(f"NIVEL {nivel_idx+1}", 20, 80, 30, config.ANCHO, config.ALTO, (200, 200, 200))
        elif estado == 2:
            utils.draw_text_2d("MUERTO", config.ANCHO//2 - 120, 250, 80, config.ANCHO, config.ALTO, (200, 0, 0))
            utils.draw_text_2d("[ENTER] REINTENTAR", config.ANCHO//2 - 160, 350, 30, config.ANCHO, config.ALTO)
        elif estado == 3:
            utils.draw_text_2d("VICTORIA", config.ANCHO//2 - 140, 250, 80, config.ANCHO, config.ALTO, (0, 255, 0))

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__": main()