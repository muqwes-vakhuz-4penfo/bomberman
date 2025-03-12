
from colores import *

# Dimensiones de la ventana
ANCHO = 650
ALTO = 700

# Número de filas y columnas de la matriz
FILAS = 14
COLUMNAS = 13


# Tamaño de cada celda de la matriz
TAMANO_CELDA = 50

ruta_fuente = "eight_bit_madness/EIGHT-BIT-MADNESS.TTF"

# Matriz 
# 0 = Libre
# 1 = Ladrillo Gris
# 2 = Player
# 3 = Enemigo
# 4 = Caja hard
# 5 = Caja random

matriz = [

    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 4, 5, 5, 5, 5, 5, 5, 0, 3, 1],
    [1, 0, 1, 5, 1, 5, 1, 5, 1, 5, 1, 0, 1],
    [1, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1],
    [1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1],
    [1, 5, 5, 5, 5, 0, 3, 0, 5, 5, 5, 5, 1],
    [1, 5, 1, 5, 1, 0, 1, 0, 1, 5, 1, 5, 1],
    [1, 5, 5, 5, 5, 0, 0, 0, 5, 5, 5, 5, 1],
    [1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1, 5, 1],
    [1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 1],
    [1, 0, 1, 5, 1, 5, 1, 5, 1, 5, 1, 0, 1],
    [1, 3, 0, 5, 5, 5, 5, 5, 5, 5, 0, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]