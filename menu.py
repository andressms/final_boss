import pygame
import numpy as np
import math
from pygame.locals import *
from OpenGL.GL import *
from pyrr import matrix44, Vector3
import config

def ejecutar_menu(shader):
    clock = pygame.time.Clock()
    running = True
    pygame.display.set_caption("MENU PRINCIPAL | ENTER=JUGAR ESC=SALIR")
    print("--- MENU ---")

    while running:
        for event in pygame.event.get():
            if event.type == QUIT: return False
            if event.type == KEYDOWN:
                if event.key == K_RETURN: return True
                if event.key == K_ESCAPE: return False

        glClearColor(0.05, 0.05, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Camara giratoria simple
        t = pygame.time.get_ticks() / 1000
        cam_x = 7.5 + np.sin(t) * 10
        cam_z = 7.5 + np.cos(t) * 10
        
        view = matrix44.create_look_at(
            np.array([cam_x, 10.0, cam_z], dtype=np.float32),
            np.array([7.5, 0.0, 7.5], dtype=np.float32),
            np.array([0.0, 1.0, 0.0], dtype=np.float32)
        )
        projection = matrix44.create_perspective_projection_matrix(50, config.ANCHO/config.ALTO, 0.1, 100)

        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection)
        
        # Dibujar Mapa de fondo (Nivel 1)
        for r, row in enumerate(config.NIVEL_1):
            for c, tile in enumerate(row):
                if tile == -1: continue
                model = matrix44.create_from_translation(Vector3([c, 0, r]))
                
                color = config.COLOR_SUELO
                if tile == 1: 
                    model = matrix44.multiply(matrix44.create_from_scale(Vector3([1, 4, 1])), model)
                    color = config.COLOR_PARED
                
                glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
                glUniform3fv(glGetUniformLocation(shader, "objectColor"), 1, color)
                glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, None)

        pygame.display.flip()
        clock.tick(60)
    return False