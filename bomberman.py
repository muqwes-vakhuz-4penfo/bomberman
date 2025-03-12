import pygame
from pygame.locals import *
import random
import sys
import sqlite3
import string
from constantes import *
from arbol_comportamiento import Nodo, Selector, Secuencia, Accion
from algoritmo_a_star import algoritmo_a_star



class Jugador(pygame.sprite.Sprite):
    def __init__(self, x, y, vidas = 3):
        super().__init__()
 
        self.imagenes_derecha = [pygame.image.load("Imagenes/personajeParado.png").convert_alpha(),
                                 pygame.image.load("Imagenes/personajeCaminando.png").convert_alpha()]
        self .imagenes_izquierda = [pygame.transform.flip(pygame.image.load("Imagenes/personajeParado.png").convert_alpha(), True, False),
                                   pygame.transform.flip(pygame.image.load("Imagenes/personajeCaminando.png").convert_alpha(), True, False)]
        self.imagenes_arriba = [pygame.image.load("Imagenes/personajeEspaldas.png").convert_alpha(),
                                 pygame.image.load("Imagenes/personajeEspaldasCaminando.png").convert_alpha()]
        self.imagenes_abajo = [pygame.image.load("Imagenes/personajedefrente.png").convert_alpha(),
                               pygame.image.load("Imagenes/personajefrentecaminando.png").convert_alpha()]
        self.imagenes_muerte = [pygame.image.load("Imagenes/muerteUno.png").convert_alpha(),
                           pygame.image.load("Imagenes/muerteDos.png").convert_alpha(),
                           pygame.image.load("Imagenes/muerteTres.png").convert_alpha()]
        self.imagen_actual = 0
        self.image = self.imagenes_derecha[self.imagen_actual]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vidas = vidas
        self.velocidad = 2
        self.hitbox = self.rect
        self.tiempo_generacion = 0
        self.puntaje = 0
        self.cantidad_bombas = 1
        self.muerto = False
        self.muerto_por_explosion = False
        self.muerto_por_enemigo = False

    def update(self, teclas):
        
        if teclas[K_SPACE]:
            self.poner_bomba()

        if teclas[K_UP]:

            self.rect.y -= self.velocidad
            self.imagen_actual = (self.imagen_actual + 1) % len(self.imagenes_arriba)
            self.image = self.imagenes_arriba[self.imagen_actual]
        elif teclas[K_DOWN]:

            self.rect.y += self.velocidad
            self.imagen_actual = (self.imagen_actual + 1) % len(self.imagenes_abajo)
            self.image = self.imagenes_abajo[self.imagen_actual]
        elif teclas[K_LEFT]:
        
            self.rect.x -= self.velocidad
            self.imagen_actual = (self.imagen_actual + 1) % len(self.imagenes_izquierda)
            self.image = self.imagenes_izquierda[self.imagen_actual]
        elif teclas[K_RIGHT]:
            
            self.rect.x += self.velocidad
            self.imagen_actual = (self.imagen_actual + 1) % len(self.imagenes_derecha)
            self.image = self.imagenes_derecha[self.imagen_actual]
        

        for bomba in juego.bombas:
            
            if teclas[K_UP] and self.rect.y == bomba.rect.y + 40 and self.rect.x in range(bomba.rect.x, bomba.rect.x + 50):
                self.rect.y += self.velocidad     
            elif teclas[K_DOWN] and self.rect.y + 30 == bomba.rect.y and self.rect.x in range(bomba.rect.x, bomba.rect.x + 50):
                self.rect.y -= self.velocidad
            elif teclas[K_LEFT] and self.rect.x -1 == bomba.rect.x + 35 and self.rect.y in range(bomba.rect.y, bomba.rect.y + 50):
                self.rect.x += self.velocidad
            elif teclas[K_RIGHT] and self.rect.x + 28== bomba.rect.x and self.rect.y in range(bomba.rect.y, bomba.rect.y + 50):
                self.rect.x -= self.velocidad        

        for bloque in juego.bloques:

            if teclas[K_UP] and self.hitbox.colliderect(bloque.hitbox):
                self.rect.y += self.velocidad
            elif teclas[K_DOWN] and self.hitbox.colliderect(bloque.hitbox):
                self.rect.y -= self.velocidad
            elif teclas[K_LEFT] and self.hitbox.colliderect(bloque.hitbox):
                self.rect.x += self.velocidad
            elif teclas[K_RIGHT] and self.hitbox.colliderect(bloque.hitbox):
                self.rect.x -= self.velocidad
                
        for caja in juego.cajas:

            if teclas[K_UP] and self.hitbox.colliderect(caja.hitbox):
                self.rect.y += self.velocidad    
            elif teclas[K_DOWN] and self.hitbox.colliderect(caja.hitbox):
                self.rect.y -= self.velocidad
            elif teclas[K_LEFT] and self.hitbox.colliderect(caja.hitbox):
                self.rect.x += self.velocidad
            elif teclas[K_RIGHT] and self.hitbox.colliderect(caja.hitbox):
                self.rect.x -= self.velocidad


        for enemigo in juego.enemigo_sprite:

            if enemigo.hitbox.colliderect(self):
                self.morir()
                self.muerto = True

        for explosion in juego.explosiones:
            if self.muerto_por_explosion == False:  
                if explosion.hitbox.colliderect(self):
                    self.morir()
                    self.muerto_por_explosion = True
          
        for powerup in juego.powerups: 
            if powerup.hitbox.colliderect(self):
                powerup.incrementar_bombas()
                powerup.kill()               
      
    def morir(self):
        muerte = pygame.mixer.Sound("Sonido/gritoMuerte.wav")
        self.vidas -= 1 
        self.image = self.imagenes_muerte[0]
        muerte.play()
        self.rect.x = 54
        self.rect.y = 104

        
        
    def poner_bomba(self):
        if pygame.sprite.spritecollideany(self, juego.bombas):
            return  # Si ya hay una bomba en la posición actual del jugador, no hace nada
        
        if len(juego.bombas) == self.cantidad_bombas:
            return
        # Calcular la posición de la matriz más cercana al jugador
        else:
            x_matriz = round(self.rect.x / TAMANO_CELDA) * TAMANO_CELDA
            y_matriz = round(self.rect.y / TAMANO_CELDA) * TAMANO_CELDA

            bomba = Bomba(x_matriz, y_matriz)
            self.muerto_por_explosion = False
            bomba.tiempo_colocacion = pygame.time.get_ticks()

            juego.bombas.add(bomba)
        
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, id):
        super().__init__()
        self.imagenes_izquierda = [pygame.image.load("Imagenes/enemigoUno.png").convert_alpha(),
                                 pygame.image.load("Imagenes/enemigoDos.png").convert_alpha()]
        self.imagenes_derecha = [pygame.transform.flip(pygame.image.load("Imagenes/enemigoUno.png").convert_alpha(), True, False),
                                   pygame.transform.flip(pygame.image.load("Imagenes/enemigoDos.png").convert_alpha(), True, False)]
        self.imagenes_arriba = [pygame.image.load("Imagenes/enemigoAtrasUno.png").convert_alpha(),
                                 pygame.image.load("Imagenes/enemigoAtrasDos.png").convert_alpha()]
        self.imagenes_abajo = [pygame.image.load("Imagenes/enemigoFrenteUno.png").convert_alpha(),
                               pygame.image.load("Imagenes/enemigoFrenteDos.png").convert_alpha()]
        self.imagen_actual = 0
        self.image = self.imagenes_derecha[self.imagen_actual]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocidad = 0.5  # Reducimos la velocidad del enemigo
        self.hitbox = self.rect
        self.muerto = False
        self.id = id
        self.cantidad_de_pasos = 0
        self.ruta = []
        self.tiempo_reaccion = pygame.time.get_ticks()

        # Crear árbol de comportamiento
        self.arbol_comportamiento = Selector([
            Secuencia([Accion(self.mover_a_jugador), Accion(self.atacar_jugador)]),
            Accion(self.patrullar)
        ])

    def update(self):
        # Añadir retraso en el tiempo de reacción
        if pygame.time.get_ticks() - self.tiempo_reaccion > 500:  # 500 milisegundos de retraso
            # Ejecutar el árbol de comportamiento
            self.arbol_comportamiento.ejecutar()
            self.tiempo_reaccion = pygame.time.get_ticks()

        # Verificar colisiones con explosiones
        for explosion in juego.explosiones:
            if self.hitbox.colliderect(explosion.hitbox):
                self.explotar()

    def mover_a_jugador(self):
        print("Ejecutando mover_a_jugador")
        jugador_pos = (juego.jugador.rect.x // TAMANO_CELDA, juego.jugador.rect.y // TAMANO_CELDA)
        enemigo_pos = (self.rect.x // TAMANO_CELDA, self.rect.y // TAMANO_CELDA)
        self.ruta = algoritmo_a_star(enemigo_pos, jugador_pos, juego.matriz)

        if self.ruta and len(self.ruta) > 1:
            siguiente_pos = self.ruta[1]  # Siguiente posición en la ruta
            self.rect.x = siguiente_pos[0] * TAMANO_CELDA
            self.rect.y = siguiente_pos[1] * TAMANO_CELDA
            return True
        return False

    def atacar_jugador(self):
        print("Ejecutando atacar_jugador")
        # Verificar si el enemigo está cerca del jugador
        distancia = abs(self.rect.x - juego.jugador.rect.x) + abs(self.rect.y - juego.jugador.rect.y)
        if distancia <= TAMANO_CELDA:  # Aumentamos la distancia de detección
            juego.jugador.recibiendo_dano = True
            return True
        return False

    def patrullar(self):
        print("Ejecutando patrullar")
        # Movimiento simple de patrullaje
        self.rect.x += self.velocidad
        if self.rect.x < 0 or self.rect.x > ANCHO:
            self.velocidad *= -1
        return True

    def explotar(self):
        # Manejar la explosión que afecta al enemigo
        self.image = self.imagenes_abajo[self.imagen_actual]  # Cambiar la imagen a una de la explosión o muerte
        self.kill()  # Eliminar al enemigo del juego
        juego.jugador.puntaje += 100  # Incrementar el puntaje del jugador



class Potenciador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Imagenes/masUnaBomba.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hitbox = self.rect
        self.sonido = pygame.mixer.Sound("Sonido/agarrarPotenciador.mp3")
    
    def incrementar_bombas(self):
        if juego.jugador.cantidad_bombas == 3:
            return
        else:
            juego.jugador.cantidad_bombas += 1
        self.sonido.play()

    def update(self):
        if juego.jugador.cantidad_bombas == 3:
            for powerup in juego.powerups:
                powerup.kill()

class Bomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.imagenes = [
            pygame.image.load("Imagenes/bombaUno.png").convert_alpha(),
            pygame.image.load("Imagenes/bombaDos.png").convert_alpha(),
            pygame.image.load("Imagenes/bombaTres.png").convert_alpha()
        ]

        self.imagen_actual = 0
        self.image = self.imagenes[self.imagen_actual]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tiempo_colocacion = 0  # Almacenar el momento en que se coloca la bomba
        self.hitbox = self.rect
        self.sonido_bomba = pygame.mixer.Sound("Sonido/ExplosiónBomba.mp3")

    def update(self):
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - self.tiempo_colocacion

        # Verificar si ha pasado el tiempo de vida de la bomba (3 segundos = 3000 milisegundos)
        if tiempo_transcurrido >= 2000:
            self.explotar()
            self.kill()  # Eliminar la bomba
        elif tiempo_transcurrido >= 1500:
            # Si han pasado 2 segundos, cambiar a la imagen de la bombaDos.png
            self.imagen_actual = 2
            self.image = self.imagenes[self.imagen_actual]
        elif tiempo_transcurrido >= 1000:
            # Si ha pasado 1 segundo, cambiar a la imagen de la bombaUno.png
            self.imagen_actual = 1
            self.image = self.imagenes[self.imagen_actual]
        elif tiempo_transcurrido >= 500:
            # Si ha pasado 1 segundo, cambiar a la imagen de la bombaUno.png
            #self.sonido_mecha.play()
            self.imagen_actual = 0
            self.image = self.imagenes[self.imagen_actual]
        
        for explosion in juego.explosiones:
            if self.hitbox.colliderect(explosion.hitbox):
                self.explotar()
                self.kill()

    def explotar(self):
        x = self.rect.x
        y = self.rect.y

        # Crear explosiones en las casillas adyacentes (arriba, abajo, izquierda, derecha)
        self.crear_explosion(x, y) #lugar de la bomba
        self.crear_explosion(x, y - TAMANO_CELDA)  # Arriba
        self.crear_explosion(x, y + TAMANO_CELDA)  # Abajo
        self.crear_explosion(x - TAMANO_CELDA, y)  # Izquierda
        self.crear_explosion(x + TAMANO_CELDA, y)  # Derecha
        self.sonido_bomba.play()

    def crear_explosion(self, x, y):
        # Obtener la posición de la matriz correspondiente a las coordenadas x, y
        fila = y // TAMANO_CELDA
        columna = x // TAMANO_CELDA
        
        # Verificar si la posición está dentro de los límites de la matriz
        if fila >= 2 and fila < FILAS and columna >= 0 and columna < COLUMNAS:
            # Verificar si la posición contiene un bloque gris
            if matriz[fila][columna] != 1:
                # Crear una explosión en la posición indicada
                explosion = Explosion(x, y)
                explosion.tiempo_aparicion = pygame.time.get_ticks()
                juego.explosiones.add(explosion)
                
                # Verificar si la posición contiene una caja
                if matriz[fila][columna] == 4 or matriz[fila][columna] == 5:
                    # Eliminar la caja de la matriz y del grupo de cajas
                    #matriz[fila][columna] = 0
                    for caja in juego.cajas:
                        if caja.id == (fila, columna): 
                            juego.cajas.remove(caja)
                            juego.jugador.puntaje += 10

                            if juego.jugador.cantidad_bombas < 3:
                                juego.crear_potenciador(columna, fila)
                                         
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.imagenes = [
            pygame.image.load("Imagenes/fuego.png").convert_alpha(),
            pygame.image.load("Imagenes/fuego.png").convert_alpha(),
            pygame.image.load("Imagenes/fuego.png").convert_alpha()
        ]

        self.imagen_actual = 0
        self.image = self.imagenes[self.imagen_actual]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hitbox = self.rect
        self.tiempo_aparicion = 0

    def update(self):
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - self.tiempo_aparicion
        # Verificar si ha pasado el tiempo de vida de la bomba (3 segundos = 3000 milisegundos)
        if tiempo_transcurrido >= 1000:
            self.kill()  # Eliminar la explosion
        elif tiempo_transcurrido >= 500:
            # Si pasó 1 segundo, cambiar a la imagen de la bombaDos.png
            self.imagen_actual = 1
            self.image = self.imagenes[self.imagen_actual]

class Bloque(pygame.sprite.Sprite):
    def __init__(self, x, y, imagen, id = (0,0)):
        super().__init__()
        self.image = pygame.image.load(imagen).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.id = id
        self.hitbox = self.rect

class Tiempo(pygame.sprite.Sprite):
    def __init__(self, tiempo_restante):
        super().__init__()
        self.tiempo_restante = tiempo_restante
        self.tiempo_general = pygame.time.get_ticks()

    def tiempo_juego(self):
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = self.tiempo_restante - tiempo_actual
        return tiempo_transcurrido 

    def mostrar_tiempo(self, pantalla, fuente):
        if juego.jugador.vidas > 0:    
            tiempo = round(self.tiempo_juego() / 1000)
            texto_tiempo = fuente.render(str(tiempo), True, BLANCO)
            pantalla.blit(texto_tiempo, (200, 15))

class Score(pygame.sprite.Sprite):
    def __init__(self):
        self.conn = ''
        self.cursor = ''
        self.lista_puntajes = []

    def conectar_base(self):

        self.conn = sqlite3.connect('puntajes.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS puntajes (nombre TEXT, puntaje INTEGER)')

    def insertar_puntaje(self, nombre, puntaje):
        self.conectar_base()
        self.cursor.execute('INSERT INTO puntajes VALUES (?, ?)', (nombre, puntaje))
        self.conn.commit()
        self.conn.close()

    def ordenar_tabla(self):
        self.conectar_base()
        consulta = "SELECT * FROM puntajes ORDER BY puntaje DESC"
        self.cursor.execute(consulta)
        resultados = self.cursor.fetchall()
        self.conn.close()
        return resultados
    
    def consultar_puntaje(self):
        resultados = self.ordenar_tabla()
        if len(resultados) < 1:
            return -1
        else:
            for fila in resultados:
                nombre = fila[0]
                puntaje = fila[1]
                self.lista_puntajes.append({'nombre': nombre,'puntaje': puntaje})
    
    def consultar_puntaje_maximo(self):
        retorno = False
        resultados = self.ordenar_tabla()
        cantidad_puntajes = len(resultados)
        if cantidad_puntajes > 5:
            cantidad_puntajes = 5
        else:
            retorno = True
        for i in range(cantidad_puntajes):
            if juego.jugador.puntaje > resultados[i][1]:
                retorno = True
        return retorno
    
class Juego:
    def __init__(self):
        
        self.ancho, self.alto = ANCHO, ALTO
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        self.reloj = pygame.time.Clock()
        self.fondo = VERDE_OSCURO
        self.matriz = [[0] * 13 for _ in range(15)]
        self.bloques = pygame.sprite.Group()
        self.cajas = pygame.sprite.Group()
        self.bombas = pygame.sprite.Group()
        self.explosiones = pygame.sprite.Group()
        self.jugador = None
        self.jugador_sprite = pygame.sprite.Group()
        self.enemigo_sprite = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.musica_nivel_uno = 0
        self.musica_nivel_dos = 0
        self.musica_nivel_tres = 0
        self.musica_end = 0
        self.bandera_entrada = False
        self.bandera_end = False
        self.nivel = 0
        self.tabla_puntajes = Score()
        
    def crear_jugador(self):
        x = 54
        y = 104
        self.jugador = Jugador(x, y)
        self.jugador_sprite.add(self.jugador)

    def crear_enemigo(self, nivel):
        cantidad_enemigos = 0
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                if matriz[fila][columna] == 3 and cantidad_enemigos < nivel:
                    x = columna * TAMANO_CELDA
                    y = fila * TAMANO_CELDA
                    self.enemigo = Enemigo(x, y, cantidad_enemigos)
                    self.enemigo_sprite.add(self.enemigo)
                    cantidad_enemigos +=1                        

    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key in self.keys:
                    self.keys[evento.key] = True
            elif evento.type == pygame.KEYUP:
                if evento.key in self.keys:
                    self.keys[evento.key] = False

    def crear_bloques(self):
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                if matriz[fila][columna] == 1:
                    x = columna * TAMANO_CELDA
                    y = fila * TAMANO_CELDA
                    bloque = Bloque(x, y, "Imagenes/bloquegris.png")
                    self.bloques.add(bloque)

    def crear_cajas(self):
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                if matriz[fila][columna] == 5:
                    numero_aleatorio = random.choice([0, 1, 2, 3, 4])
                    if numero_aleatorio == 0 or numero_aleatorio == 1 or numero_aleatorio == 2 or numero_aleatorio == 3:
                        x = columna * TAMANO_CELDA
                        y = fila * TAMANO_CELDA
                        caja = Bloque(x, y, "Imagenes/cajas.png", (fila, columna))
                        self.cajas.add(caja)
                elif matriz[fila][columna] == 4:
                    x = columna * TAMANO_CELDA
                    y = fila * TAMANO_CELDA
                    caja = Bloque(x, y, "Imagenes/cajas.png", (fila, columna))
                    self.cajas.add(caja)

    def crear_potenciador(self, columna, fila):
        numero_aleatorio = random.choice([0,1,2,3,4,5,6,7,8,9])
        if numero_aleatorio == 0:
            x = columna * TAMANO_CELDA
            y = fila * TAMANO_CELDA
            powerup = Potenciador(x, y)
            self.powerups.add(powerup)

    def end(self, pantalla, fuente):
        tiempo = self.temporizador.tiempo_juego()
        if self.jugador.vidas < 1 or tiempo < 1 or self.nivel == 4 :

            self.musica_nivel_uno.stop()
            self.musica_nivel_dos.stop()
            self.musica_nivel_tres.stop()
            if self.jugador.vidas > 0 and tiempo > 0:
                COLOR = VERDE
                es_top_cinco = self.tabla_puntajes.consultar_puntaje_maximo()
                self.musica_end = pygame.mixer.Sound("Sonido/musicaVictoria.mp3")
                if es_top_cinco:
                    self.musica_end.play()
                    records = self.guardar_records(fuente)
                    if records == 0:
                        print("Puntaje guardado con éxito")

            else:
                COLOR = ROJO
                self.musica_end = pygame.mixer.Sound("Sonido/findeljuego.mp3")
                self.musica_end.set_volume(0.2)
                self.musica_end.play()
            pantalla.fill((0, 0, 0))
            texto_puntaje = fuente.render("Final score: "+ str(self.jugador.puntaje), True, BLANCO)
            texto_puntaje_rect = texto_puntaje.get_rect()
            texto_puntaje_rect.center = (ANCHO/2, ALTO - 200)
            fuente = pygame.font.Font(ruta_fuente, 70) 
            texto_game_over = fuente.render("Game Over", True, COLOR)
            game_over_rect = texto_game_over.get_rect()
            game_over_rect.center = (ANCHO/2, 150)
            pantalla.blit(texto_puntaje, texto_puntaje_rect)
            pantalla.blit(texto_game_over, game_over_rect)
            
            if self.bandera_end == False:
                fuente = pygame.font.Font(ruta_fuente, 36)
                self.bandera_end = True
                # self.musica_end.set_volume(0.2)
                # self.musica_end.play()
                for bloque in self.bloques:
                    bloque.kill()
                for caja in self.cajas:
                    caja.kill()
                for explosion in self.explosiones:
                    explosion.kill()
                for jugador in self.jugador_sprite:
                    jugador.kill()
                self.temporizador.kill()
                sonido_menu = pygame.mixer.Sound("Sonido/sonidoMenu.mp3")
                sonido_seleccion = pygame.mixer.Sound("Sonido/SeleccionOpcion.mp3")
                opciones_menu = ["Back to menu", "Exit"]
                opcion_seleccionada = 0
                while True:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_UP:
                                sonido_menu.play()
                                opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones_menu)
                            elif evento.key == pygame.K_DOWN:
                                sonido_menu.play()
                                opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones_menu)
                            elif evento.key == pygame.K_RETURN:
                                sonido_seleccion.play()
                                if opcion_seleccionada == 0:  # Jugar
                                    print("Opción seleccionada: Volver al menu")
                                    self.bandera_entrada = False
                                    self.bandera_end = False
                                    return 0
                                elif opcion_seleccionada == 1:  # Salir
                                    pygame.quit()
                                    sys.exit()


                    # Renderizar las opciones del menú
                    for i, opcion in enumerate(opciones_menu):
                        if i == opcion_seleccionada:
                            texto = fuente.render(opcion, True, VERDE)
                        else:
                            texto = fuente.render(opcion, True, BLANCO)

                        rectangulo_texto = texto.get_rect()
                        rectangulo_texto.center = (ANCHO // 2, (ALTO // 2) + i * 50)
                        pantalla.blit(texto, rectangulo_texto)

                    # Actualizar la pantalla
                    pygame.display.flip()
            pygame.display.flip()
        else:
            self.musica_end.stop()
            return False

    def guardar_records(self, fuente):
        letras = list(string.ascii_uppercase)
        # Posiciones iniciales de las letras
        posicion_linea = 0
        letra_linea1 = letras[0]
        letra_linea2 = letras[0]
        letra_linea3 = letras[0]

        # Variable para almacenar el nombre del jugador
        nombre_jugador = ""
        guardando = True
        while guardando:
            for event in pygame.event.get():  
                if event.type == pygame.KEYDOWN:
                    # Cambiar entre las líneas
                    if event.key == pygame.K_LEFT:
                        posicion_linea = (posicion_linea - 1) % 3
                    elif event.key == pygame.K_RIGHT:
                        posicion_linea = (posicion_linea + 1) % 3
                    # Selección de letras con las flechas arriba y abajo
                    elif event.key == pygame.K_UP:
                        if posicion_linea == 0:
                            letra_linea1 = letras[(letras.index(letra_linea1) - 1) % len(letras)]
                        elif posicion_linea == 1:
                            letra_linea2 = letras[(letras.index(letra_linea2) - 1) % len(letras)]
                        elif posicion_linea == 2:
                            letra_linea3 = letras[(letras.index(letra_linea3) - 1) % len(letras)]
                    elif event.key == pygame.K_DOWN:
                        if posicion_linea == 0:
                            letra_linea1 = letras[(letras.index(letra_linea1) + 1) % len(letras)]
                        elif posicion_linea == 1:
                            letra_linea2 = letras[(letras.index(letra_linea2) + 1) % len(letras)]
                        elif posicion_linea == 2:
                            letra_linea3 = letras[(letras.index(letra_linea3) + 1) % len(letras)]
                    # Concatenar las letras al presionar Enter
                    elif event.key == pygame.K_RETURN:
                        nombre_jugador = letra_linea1 + letra_linea2 + letra_linea3
                        self.tabla_puntajes.insertar_puntaje(nombre_jugador,self.jugador.puntaje)
                        return 0

            # Limpiar la pantalla con color negro
            self.pantalla.fill(NEGRO)

            # Renderizar las letras en las líneas correspondientes
            texto_record = fuente.render("Input your initials", True, BLANCO)
            texto_record_rect = texto_record.get_rect()
            texto_record_rect.center = (ANCHO/2, 300)
            texto_guardar = fuente.render("NEW RECORD!", True, BLANCO)
            texto_guardar_rect = texto_guardar.get_rect()
            texto_guardar_rect.center = (ANCHO/2, 200)
            texto_linea1 = fuente.render(letra_linea1, True, BLANCO if posicion_linea != 0 else VERDE)
            texto_linea2 = fuente.render(letra_linea2, True, BLANCO if posicion_linea != 1 else VERDE)
            texto_linea3 = fuente.render(letra_linea3, True, BLANCO if posicion_linea != 2 else VERDE)

            # Posición x inicial para las letras
            x = (ANCHO / 2) - 50
            # Posición y para todas las líneas
            y = ALTO / 2

            # Espacio entre las letras
            espacio = 20

            # Mostrar las letras una al lado de la otra
            self.pantalla.blit(texto_guardar, texto_guardar_rect)
            self.pantalla.blit(texto_record, texto_record_rect)
            self.pantalla.blit(texto_linea1, (x, y))
            self.pantalla.blit(texto_linea2, (x + fuente.get_height() + espacio, y))
            self.pantalla.blit(texto_linea3, (x + 2 * (fuente.get_height() + espacio), y))

            # Actualizar la ventana
            pygame.display.flip()

    def mostrar_records(self, fuente):
        self.tabla_puntajes.lista_puntajes.clear()
        self.pantalla.fill(NEGRO)
        self.tabla_puntajes.consultar_puntaje()
        cantidad_puntajes = len(self.tabla_puntajes.lista_puntajes)
        if cantidad_puntajes != 0:
            if cantidad_puntajes > 5:
                cantidad_puntajes = 5
            i = 0
            highscores = fuente.render("HIGHSCORES", True, ROJO)
            self.pantalla.blit(highscores, (230, 90))
            for jugador in range(cantidad_puntajes):
                print(self.tabla_puntajes.lista_puntajes[jugador])
                x = (ANCHO / 2)
                y = 150
                print(jugador)
                if jugador == 0:
                    color = AZUL_OSCURO
                else:
                    color = ROSA
                nombre = fuente.render(str(self.tabla_puntajes.lista_puntajes[jugador]['nombre']), True, color)
                self.pantalla.blit(nombre, (x - 200, y + (i*100)))
                puntaje = fuente.render(str(self.tabla_puntajes.lista_puntajes[jugador]['puntaje']), True, color)
                self.pantalla.blit(puntaje, (x + 100, y + (i*100)))
                
                fuente = pygame.font.Font(ruta_fuente, 30) 
                press_enter = fuente.render("Press enter to return", True, BLANCO)
                press_enter_rect = press_enter.get_rect()
                press_enter_rect.center = (ANCHO/2, ALTO/2 + 300)
                self.pantalla.blit(press_enter, press_enter_rect)
                fuente = pygame.font.Font(ruta_fuente, 36)
                self.pantalla.blit(press_enter, press_enter_rect)
                oro = pygame.image.load("Imagenes/medallaOro.png")
                self.pantalla.blit(oro, (x - 270, y - 10))
                pygame.display.flip()
                i += 1
            pygame.display.flip()
        else:
            txt = fuente.render("No records to display, be the first!", True, BLANCO)
            txt_rect = txt.get_rect()
            txt_rect.center = (ANCHO/2, ALTO/2)
            self.pantalla.blit(txt, txt_rect)
            fuente = pygame.font.Font(ruta_fuente, 30) 
            press_enter = fuente.render("Press enter to return", True, BLANCO)
            press_enter_rect = press_enter.get_rect()
            press_enter_rect.center = (ANCHO/2, ALTO/2 + 300)
            self.pantalla.blit(press_enter, press_enter_rect)
            fuente = pygame.font.Font(ruta_fuente, 36)
            pygame.display.flip()

        while True:
            for event in pygame.event.get():      
                if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return False
        
    def mostrar_vidas(self, pantalla):
        self.imagen_vida = pygame.image.load("Imagenes/vidas.png")
        for i in range(self.jugador.vidas):
            x = ANCHO - (i + 1) * (self.imagen_vida.get_width() + 10)
            y = 10
            pantalla.blit(self.imagen_vida, (x, y))
   
    def mostrar_bombas(self):
        self.imagen_bomba = pygame.image.load("Imagenes/bombaUno.png")
        for i in range(self.jugador.cantidad_bombas):
            x = ANCHO + (i + 1) * (self.imagen_bomba.get_width() + 5) - 400
            y = 5
            self.pantalla.blit(self.imagen_bomba, (x, y))

    def crear_tiempo(self, tiempo):
        tiempo_pasado = pygame.time.get_ticks()
        tiempo_neto = tiempo_pasado + tiempo
        self.temporizador = Tiempo(tiempo_neto)

    def mostrar_puntaje(self, pantalla, fuente, x, y):
        if self.jugador.vidas > 0:    
            texto_puntaje = fuente.render(str(self.jugador.puntaje), True, BLANCO)
            pantalla.blit(texto_puntaje, (x, y))

    def menu_inicial(self, pantalla, fuente):
        if self.bandera_entrada == False:
            musica = pygame.mixer.Sound("Sonido/musicaMenu.mp3")
            self.bandera_entrada = True
            self.musica_end.stop()
        sonido_menu = pygame.mixer.Sound("Sonido/sonidoMenu.mp3")
        sonido_seleccion = pygame.mixer.Sound("Sonido/SeleccionOpcion.mp3")
        opciones_menu = ["Play", "Leaderboard", "Exit"]
        opcion_seleccionada = 0
        musica.play()
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        sonido_menu.play()
                        opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones_menu)
                    elif evento.key == pygame.K_DOWN:
                        sonido_menu.play()
                        opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones_menu)
                    elif evento.key == pygame.K_RETURN:
                        sonido_seleccion.play()
                        if opcion_seleccionada == 0:  # Jugar
                            print("Opción seleccionada: Jugar")
                            pantalla.fill((0, 0, 0))
                            musica.stop()
                            texto_nivel = fuente.render("LEVEL 1", True, BLANCO)
                            pantalla.blit(texto_nivel, (ANCHO/2 - 50, ALTO/2))
                            pygame.display.flip()
                            pygame.time.delay(2000)
                            self.bandera_entrada = False
                            return 1
                        elif opcion_seleccionada == 1:  # Puntaje
                            self.mostrar_records(fuente)
                            #return 5
                        elif opcion_seleccionada == 2:  # Salir
                            pygame.quit()
                            sys.exit()

            pantalla.fill(NEGRO)
            fuente = pygame.font.Font(ruta_fuente, 36)
            # Renderizar las opciones del menú
            for i, opcion in enumerate(opciones_menu):
                if i == opcion_seleccionada:
                    texto = fuente.render(opcion, True, VERDE)
                else:
                    texto = fuente.render(opcion, True, BLANCO)
                titulo = pygame.image.load("Imagenes/titulo.png")
                titulo_rect = titulo.get_rect()
                titulo_rect.center = ( ANCHO / 2 + 15, ALTO - 550)
                
                rectangulo_texto = texto.get_rect()
                rectangulo_texto.center = (ANCHO // 2, (ALTO // 2) + i * 50)
                pantalla.blit(texto, rectangulo_texto)
                pantalla.blit(titulo, titulo_rect)
            fuente = pygame.font.Font(ruta_fuente, 30) 
            press_enter = fuente.render("Press enter to select", True, BLANCO)
            press_enter_rect = press_enter.get_rect()
            press_enter_rect.center = (ANCHO/2, ALTO/2 + 200)
            pantalla.blit(press_enter, press_enter_rect)
            fuente = pygame.font.Font(ruta_fuente, 20)  
            copy = fuente.render("TM & Cº 1993 HUDSON SOFT \n Licensed by Mauro Panzini from 1F", True, BLANCO)
            rect_copy = copy.get_rect()
            rect_copy.center = (ANCHO/2, ALTO - 20)
            pantalla.blit(copy, rect_copy)
            fuente = pygame.font.Font(ruta_fuente, 36)
            # Actualizar la pantalla
            pygame.display.flip()

    def nivel_general(self, fuente):
        teclas = pygame.key.get_pressed()
        self.jugador.update(teclas)  # Mover al jugador según la velocidad establecida
        self.enemigo.update()
        self.pantalla.fill(self.fondo)
        self.enemigo_sprite.draw(self.pantalla)
        self.powerups.draw(self.pantalla)
        self.bloques.draw(self.pantalla)
        self.cajas.draw(self.pantalla)
        self.jugador_sprite.draw(self.pantalla)  # Dibujar al jugador en la pantalla
        self.explosiones.draw(self.pantalla)
        self.explosiones.update()
        self.powerups.update()
        self.bombas.update()  # Actualizar el estado de las bombas
        self.bombas.draw(self.pantalla)  # Dibujar las bombas en la pantalla
        self.mostrar_vidas(self.pantalla)
        self.mostrar_bombas()
        self.mostrar_puntaje(self.pantalla, fuente, 15, 15)
        self.temporizador.mostrar_tiempo(self.pantalla, fuente)
        tiempo_restante = self.temporizador.tiempo_juego()
        pygame.display.flip()
        if self.jugador.vidas < 1 or tiempo_restante < 1:
            for bloque in self.bloques:
                bloque.kill()
            for caja in self.cajas:
                caja.kill()
            for explosion in self.explosiones:
                explosion.kill()
            self.temporizador.kill()
            for enemigo in self.enemigo_sprite:
                enemigo.kill()
            return -1
        return tiempo_restante

    def nivel_uno(self, pantalla, fuente):
        if self.bandera_entrada == False:
            for explosion in self.explosiones:
                explosion.kill()
            for bomba in self.bombas:
                bomba.kill()
            self.musica_nivel_uno.play()
            self.crear_bloques()
            self.crear_cajas()
            self.crear_enemigo(self.nivel)
            self.crear_jugador()
            self.crear_tiempo(45000)
            self.bandera_entrada = True
        
        tiempo_restante = self.nivel_general(fuente)
        if tiempo_restante == -1:
            return 4
        
        if len(self.enemigo_sprite) == 0:
            self.jugador.puntaje += int(tiempo_restante / 100)
            self.musica_nivel_uno.stop()
            self.bandera_entrada = False
            pantalla.fill(NEGRO)
            for bloque in self.bloques:
                bloque.kill()
            for caja in self.cajas:
                caja.kill()
            for explosion in self.explosiones:
                explosion.kill()
            for potenciador in self.powerups:
                potenciador.kill()
            self.temporizador.kill()
            
            pantalla.fill((0, 0, 0))
            texto_nivel = fuente.render("LEVEL 2", True, BLANCO)
            pantalla.blit(texto_nivel, (ANCHO/2 - 50, ALTO/2))
            pygame.display.flip()
            pygame.time.delay(3000)
            return 2
        else:
            return 1

    def nivel_dos(self, pantalla, fuente):
        if self.bandera_entrada == False:
            for explosion in self.explosiones:
                explosion.kill()
            for bomba in self.bombas:
                bomba.kill()
            self.fondo = AZUL_OSCURO
            self.musica_nivel_dos.play(1)
            pantalla.fill(NEGRO)
            self.crear_bloques()
            self.crear_cajas()
            self.crear_enemigo(self.nivel)
            self.crear_tiempo(60000)
            self.jugador.rect.x = 54
            self.jugador.rect.y = 104
            self.bandera_entrada = True
        
        tiempo_restante = self.nivel_general(fuente)
        if tiempo_restante == -1:
            return 4
        
        if self.jugador.vidas < 1 or tiempo_restante < 1:
            for bloque in self.bloques:
                bloque.kill()
            for caja in self.cajas:
                caja.kill()
            for explosion in self.explosiones:
                explosion.kill()
            for enemigo in self.enemigo_sprite:
                enemigo.kill()
            for potenciador in self.powerups:
                potenciador.kill()
            self.temporizador.kill()
            return 4
        
        if len(self.enemigo_sprite) == 0:
            self.jugador.puntaje += int(tiempo_restante / 100)
            self.bandera_entrada = False
            self.musica_nivel_dos.stop()
            pantalla.fill(NEGRO)
            for bloque in self.bloques:
                bloque.kill()
            for caja in self.cajas:
                caja.kill()
            for explosion in self.explosiones:
                explosion.kill()
            self.temporizador.kill()
            pantalla.fill((0, 0, 0))
            texto_nivel = fuente.render("LEVEL 3", True, BLANCO)
            pantalla.blit(texto_nivel, (ANCHO/2 - 50, ALTO/2))
            pygame.display.flip()
            pygame.time.delay(3000)
            return 3
        else:
            return 2

    def nivel_tres(self, pantalla, fuente):
        if self.bandera_entrada == False:
            for explosion in self.explosiones:
                explosion.kill()
            for bomba in self.bombas:
                bomba.kill()
            self.fondo = ROJO
            pantalla.fill(NEGRO)
            self.musica_nivel_tres.play()
            self.crear_bloques()
            self.crear_cajas()
            self.crear_enemigo(self.nivel + 1)
            self.crear_tiempo(90000)
            self.jugador.rect.x = 54
            self.jugador.rect.y = 104
            self.bandera_entrada = True
        
        tiempo_restante = self.nivel_general(fuente)
        if tiempo_restante == -1:
            return 4
        
        if self.jugador.vidas < 1 or tiempo_restante < 1:
            for bloque in self.bloques:
                bloque.kill()
            for caja in self.cajas:
                caja.kill()
            for explosion in self.explosiones:
                explosion.kill()
            for enemigo in self.enemigo_sprite:
                enemigo.kill()
            for potenciador in self.powerups:
                potenciador.kill()
            self.temporizador.kill()
            return 4
        if len(self.enemigo_sprite) == 0:
            self.jugador.puntaje += int(tiempo_restante / 100)
            self.bandera_entrada = False
            self.musica_nivel_tres.stop()

            pantalla.fill(NEGRO)
            for bloque in self.bloques:
                bloque.kill()
            for caja in self.cajas:
                caja.kill()
            for explosion in self.explosiones:
                explosion.kill()
            self.temporizador.kill()

            return 4
        else:
            return 3

    def ejecutar(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        fuente = pygame.font.Font(ruta_fuente, 36)      
        pygame.display.set_caption("BomberMan!")
        corriendo = True
        self.musica_nivel_uno = pygame.mixer.Sound("Sonido/musicaNivelUno.mp3") 
        self.musica_nivel_dos = pygame.mixer.Sound("Sonido/musicaNivelDos.mp3") 
        self.musica_nivel_tres = pygame.mixer.Sound("Sonido/musicaNivelTres.mp3") 
        self.musica_end = pygame.mixer.Sound("Sonido/findeljuego.mp3")
        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False

            if self.nivel == 0:
                self.nivel = self.menu_inicial(self.pantalla, fuente)
            
            elif self.nivel == 1:
                self.nivel = self.nivel_uno(self.pantalla, fuente)

            elif self.nivel == 2:
                self.nivel = self.nivel_dos(self.pantalla, fuente)
            
            elif self.nivel == 3:
                self.nivel = self.nivel_tres(self.pantalla, fuente)

            elif self.nivel == 4:
                self.nivel = self.end(self.pantalla, fuente)
            
            elif self.nivel == 5:
                self.nivel = self.mostrar_records(fuente)

            self.reloj.tick(60)

    pygame.quit()

juego = Juego()
juego.ejecutar()