import numpy as np
import pygame
from pyrr import Vector3, matrix44
import config

class Camera:
    def __init__(self):
        # Y = 1.5 FIJO (Altura de ojos)
        self.pos = np.array([1.5, 1.5, 1.5], dtype=np.float32)
        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.right = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        self.yaw = -90.0
        self.pitch = 0.0
        self.vidas = 3

    def get_view_matrix(self):
        return matrix44.create_look_at(self.pos, self.pos + self.front, self.up)

    def update_physics(self, mapa):
        # SOLO detectamos pinchos, ya no hay caidas ni saltos
        gx = int(self.pos[0])
        gz = int(self.pos[2])
        
        bloque = 0
        if 0 <= gz < len(mapa) and 0 <= gx < len(mapa[0]):
            bloque = mapa[gz][gx]
        
        if bloque == 2: return "PINCHO"
        return "OK"

    def input(self, keys, mouse_rel, mapa):
        # 1. ROTACION (Mouse)
        self.yaw += mouse_rel[0] * config.SENSIBILIDAD
        self.pitch -= mouse_rel[1] * config.SENSIBILIDAD
        self.pitch = np.clip(self.pitch, -89, 89)
        
        rad_yaw = np.radians(self.yaw); rad_pitch = np.radians(self.pitch)
        self.front = np.array([
            np.cos(rad_yaw) * np.cos(rad_pitch),
            np.sin(rad_pitch),
            np.sin(rad_yaw) * np.cos(rad_pitch)
        ], dtype=np.float32)
        
        # Normalizar vectores
        norma = np.linalg.norm(self.front)
        if norma > 0: self.front /= norma
        self.right = np.cross(self.front, self.up)
        self.right /= np.linalg.norm(self.right)

        # 2. MOVIMIENTO (Teclas WASD)
        vel = config.VELOCIDAD_JUGADOR
        pos_vieja_x = self.pos[0]
        pos_vieja_z = self.pos[2]
        
        # Movimiento solo en plano XZ (sin volar)
        mov_f = np.array([self.front[0], 0, self.front[2]], dtype=np.float32)
        if np.linalg.norm(mov_f) > 0: mov_f /= np.linalg.norm(mov_f)
        
        desp = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        if keys[pygame.K_w]: desp += mov_f * vel
        if keys[pygame.K_s]: desp -= mov_f * vel
        if keys[pygame.K_a]: desp -= self.right * vel
        if keys[pygame.K_d]: desp += self.right * vel
        
        self.pos += desp

        # 3. COLISIONES (Paredes)
        gx = int(self.pos[0])
        gz = int(self.pos[2])

        if 0 <= gz < len(mapa) and 0 <= gx < len(mapa[0]):
            if mapa[gz][gx] == 1: # Si entramos en pared, regresamos
                self.pos[0] = pos_vieja_x
                self.pos[2] = pos_vieja_z