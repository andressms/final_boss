import numpy as np
import random

ANCHO, ALTO = 1280, 720
TITULO = "NEON SURVIVOR: FINAL BOSS"

# --- CONFIGURACIÓN ---
SENSIBILIDAD = 0.30      
VELOCIDAD_JUGADOR = 0.1
# ¡MUCHO MÁS LENTO! (Antes 0.035)
VELOCIDAD_ENEMIGO = 0.015 
GRAVEDAD = 0.01

# Estados
MENU = 0
JUGANDO = 1
GAMEOVER = 2
VICTORIA = 3

# Colores
COLOR_FONDO = (5, 5, 15, 255)
COLOR_PARED = np.array([0.1, 0.9, 1.0], dtype=np.float32)
COLOR_SUELO = np.array([0.1, 0.1, 0.2], dtype=np.float32)
COLOR_ENEMIGO = np.array([1.0, 0.0, 0.0], dtype=np.float32)
COLOR_META = np.array([0.0, 1.0, 0.0], dtype=np.float32)
COLOR_PINCHO = np.array([1.0, 0.6, 0.0], dtype=np.float32)

def generar_nivel(ancho, alto, dificultad=1):
    mapa = [[1 for _ in range(ancho)] for _ in range(alto)]
    for y in range(1, alto-1):
        for x in range(1, ancho-1):
            if random.random() > 0.2: mapa[y][x] = 0
            if mapa[y][x] == 0:
                roll = random.random()
                if roll < 0.10 * dificultad: mapa[y][x] = 2 
    
    mapa[1][1] = 0; mapa[1][2] = 0
    mapa[alto-2][ancho-2] = 3
    mapa[alto//2][ancho//2] = 4
    return mapa

NIVEL_1 = generar_nivel(15, 15, 1)
NIVEL_2 = generar_nivel(20, 20, 2)
MAPAS = [NIVEL_1, NIVEL_2]