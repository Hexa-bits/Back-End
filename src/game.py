from src.models.events import Event
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard, Move
from src.models.fichas_cajon import FichaCajon
from src.models.utils import *
from src.models.patrones_figuras_matriz import pictureCardsFigures, generar_rotaciones
from pydantic import BaseModel
from typing import List, Dict, Tuple, Any
from typing import List, Tuple
import numpy as np

def detectar_patrones(matriz, patrones) -> List[List[Tuple[int, int]]]:
    """Función para detectar figuras usando Sliding Window (No checkea que no tengan 1s adyacentes, solo si coinciden con el patrón)
    Devuelve una lista de listas de coordenadas de las figuras detectadas.
    """

    filas, columnas = matriz.shape
    figuras_detectadas = []  # Almacena las posiciones de las figuras encontradas
    
    # Recorrer cada patrón
    for patron in patrones:
        p_filas, p_columnas = patron.shape  # Tamaño del patrón

        # Desplazar la ventana sobre la matriz
        for i in range(filas - p_filas + 1):
            for j in range(columnas - p_columnas + 1):
                # Extraer la submatriz de la ventana deslizante
                submatriz = matriz[i:i + p_filas, j:j + p_columnas]
                
                # Comparar submatriz con el patrón
                if np.array_equal(submatriz, patron):
                    # Si coinciden, guardar las coordenadas
                    coords = [(i + x, j + y) for x in range(p_filas) for y in range(p_columnas) if patron[x, y] == 1]
                    figuras_detectadas.append(coords)

    return figuras_detectadas

def figura_valida(matriz, coords_validas) -> bool:
    """Funcion que retorna True si la figura es válida, False en caso contrario"""

    filas, columnas = matriz.shape
    coordenadas_set = set(coords_validas)  # Convertir la lista en un set para búsquedas rápidas
    
    # Direcciones de los 4 vecinos adyacentes: arriba, abajo, izquierda, derecha
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for coord in coords_validas:
        x, y = coord
        
        # Revisar vecinos en las 4 direcciones
        for dx, dy in direcciones:
            nx, ny = x + dx, y + dy
            
            # Si el vecino está dentro de los límites de la matriz
            if 0 <= nx < filas and 0 <= ny < columnas:
                # Si el vecino es del mismo color y no está en la lista de coordenadas válidas
                if matriz[nx, ny] == matriz[x, y] and (nx, ny) not in coordenadas_set:
                    return False  # Hay un 1 no válido adyacente
    return True  # Todos los vecinos son válidos

def separar_matrices_por_color(matriz, lista_colores) -> List[np.ndarray]:
    """Separa la matriz de colores en matrices individuales por color.
    Toma como elementos:
    matriz: Una matriz numpy donde cada elemento representa un color.
    lista_colores: Una lista de colores presentes en la matriz.
    
    Devuelve una lista de matrices numpy, donde cada matriz representa un color.
    """

    # Obtener las dimensiones de la matriz
    filas, columnas = matriz.shape

    # Crear una lista vacía para almacenar las matrices de colores
    matrices_colores = []   
    # Iterar sobre cada color
    for color in lista_colores:
        # Crear una matriz de ceros con las mismas dimensiones
        matriz_color = np.zeros((filas, columnas))
        # Asignar 1 en las posiciones donde el color coincide (matriz==color)
        matriz_color[matriz == color] = 1
        # Agregar la matriz de color a la lista
        matrices_colores.append(matriz_color)   
    return matrices_colores 


class GameManager:
    """
    Usamos una sola instancia de tablero en BD
    Llevamos un registro en la clase GameManager
    Para llevar un control de si es un tablero parcial o real
    Y todas las cartas y fichas usadas en el tablero parcial
    """    

    def __init__(self):
        # Diccionario que guarda el estado de cada juego usando el game_id
        self.games: Dict[int, Any] = {}

    def create_game(self, game_id: int) -> None:
        """Agregamos un nuevo juego al GameManager cuando se inicia la partida"""
        
        # Crear una entrada para un nuevo juego con game_id
        self.games[game_id] = {
            'es_tablero_parcial': False,  # booleano que indica si el tablero usado es parcial o real
            'cartas_y_fichas_usadas': [],  # stack para apilar el carta_mov_id:int usada y par de coord(x,y) de fichas utilizadas ((x,y), (x,y))
                                            # e.g.: [(carta_mov_id, ((x,y),(x,y)), (carta_mov_id, ((x,y),(x,y)), ...]
            'jugador_en_turno_id': 0  # player_id:int del jugador en turno actual
        }

    def delete_game(self, game_id: int) -> None:
        """Eliminamos un juego del GameManager cuando se termina la partida (Alguien gana por abandono por ahora)"""
        
        # Eliminar el juego con game_id
        del self.games[game_id]


    def is_tablero_parcial(self, game_id: int) -> bool:
        """Sirve para saber si el tablero es parcial o real al enviar el tablero a Frontend"""
        
        # Obtener si el tablero es parcial
        if game_id in self.games:
            return self.games[game_id]['es_tablero_parcial']
        else: 
            return False


    def apilar_carta_y_ficha(self, game_id: int, carta_mov_id: int, 
                            dupla_coords_ficha: tuple[Coords, Coords]) -> None:
        """
        Apilar carta y par de fichas sirve para guardar cual fue el cambio parcial realizado
        Siempre me convierte el tablero en parcial
        """
        # Apilar la carta usada y par de ficha utilizada en el stack
        self.games[game_id]['cartas_y_fichas_usadas'].append((carta_mov_id, dupla_coords_ficha))
        self.games[game_id]['es_tablero_parcial'] = True

    def desapilar_carta_y_ficha(self, game_id: int) -> tuple[int, tuple[Coords, Coords]]:
        """
        Desapilar carta y par de fichas sirve para deshacer el cambio parcial realizado
        Si el stack queda vacio, me convierte el tablero en real
        Si termina el turno y no se formó figura, se debe desapilar, revertir el movimiento de fichas y devolver la carta_mov al jugador
        Hasta que el stack quede vacio, osea, hasta que el tablero sea real
        Desapilar la carta usada y par de ficha utilizada en el stack
        """

        tupla_carta_fichas = None

        if self.games[game_id]['es_tablero_parcial']:
            tupla_carta_fichas = self.games[game_id]['cartas_y_fichas_usadas'].pop()
            
            if self.games[game_id]['cartas_y_fichas_usadas'] == []:
                self.games[game_id]['es_tablero_parcial'] = False

        return tupla_carta_fichas
    
    def top_tupla_carta_y_fichas(self, game_id: int) -> tuple[int, tuple[Coords, Coords]]:
        """
        Obtiene la ultima carta y par de fichas parciales que se jugaron
        Si no hay tableros parciales, devuelve None  
        """
        tupla_carta_fichas = None
        
        if self.games[game_id]['es_tablero_parcial']:
            tupla_carta_fichas = self.games[game_id]['cartas_y_fichas_usadas'][-1]
        
        return tupla_carta_fichas


    def limpiar_cartas_fichas(self, game_id: int) -> None:
        """
        Limpiar cartas y fichas sirve para deshacernos del stack en caso haber formado figura
        Nos convierte el tablero en real
        """
        # Limpiar el stack de cartas y fichas
        self.games[game_id]['cartas_y_fichas_usadas'] = []
        self.games[game_id]['es_tablero_parcial'] = False

    def obtener_jugador_en_turno_id(self, game_id: int) -> int:
        """
        Obtener el jugador en turno
        Sirve para saber que a que jugador devolverle la carta en caso de cancelar mov parcial
        """

        return self.games[game_id]['jugador_en_turno_id']

    def set_jugador_en_turno_id(self, game_id: int, jugador_id: int) -> None:
        """Cambiar el jugador en turno"""
        self.games[game_id]['jugador_en_turno_id'] = jugador_id


def is_valid_move(movementCard: MovementCard, coords: Tuple[Coords]) -> bool:
    distancia_x = abs(coords[0].x_pos-coords[1].x_pos)
    distancia_y = abs(coords[0].y_pos-coords[1].y_pos)

    if movementCard.movimiento == Move.linea_contiguo:
        return (distancia_y == 0 and distancia_x == 1) or (distancia_y == 1 and distancia_x == 0)
    
    elif movementCard.movimiento == Move.linea_con_espacio:
        return (distancia_y == 0 and distancia_x == 2) or (distancia_y == 2 and distancia_x == 0)
    
    elif movementCard.movimiento == Move.diagonal_contiguo:
        return distancia_y == 1 and distancia_x == 1
    
    elif movementCard.movimiento == Move.diagonal_con_espacio:
        return distancia_y == 2 and distancia_x == 2
    
    elif movementCard.movimiento == Move.linea_al_lateral:
        return ((distancia_y == 0 and 1 <= distancia_x <= 5 and 
                (coords[0].x_pos==1 or coords[1].x_pos==1 or coords[0].x_pos==6 or coords[1].x_pos==6)) #Alguna de las fichas tiene
                or                                                                                      #que estar en los extremos
                (1 <= distancia_y <= 5 and distancia_x == 0 and
                (coords[0].y_pos==1 or coords[1].y_pos==1 or coords[0].y_pos==6 or coords[1].y_pos==6))) #Idem
    
    else:
        max_x_tuple = max(coords, key=lambda coord: coord.x_pos)       #
        min_x_tuple = min(coords, key=lambda coord: coord.x_pos)       #Para poder diferenciar los movimientos L

        distancia_entre_fichas_ejeY = max_x_tuple.y_pos-min_x_tuple.y_pos
        
        if movementCard.movimiento == Move.L_derecha:
            return ( ((distancia_y == 1 and distancia_x == 2) and (distancia_entre_fichas_ejeY>0)) #<-- Desde la perspectiva de la 
                    or ((distancia_y == 2 and distancia_x == 1) and distancia_entre_fichas_ejeY<0) )    #ficha de mas abajo del tablero
                                                                                                        #es como que "volves"
                                                                                                        #en columna
        elif movementCard.movimiento == Move.L_izquierda:
            return ( ((distancia_y == 1 and distancia_x == 2) and (distancia_entre_fichas_ejeY<0)) #<-- Idem pero al contrario
                    or ((distancia_y == 2 and distancia_x == 1) and distancia_entre_fichas_ejeY>0) )   #es como que "vas para adelante"             
                 
    return False


def is_valid_picture_card(pictureCard: PictureCard, coords: List[Coords]) -> bool:
    """
    Devuelve un booleano que indica si la figura de la carta coincide con la figura formada dada por las coordenadas
    en el tablero.
    """
    fig_value = pictureCard.figura.value
    figures = pictureCardsFigures()
    figure = figures[fig_value - 1]
    
    max_x = max(coords, key=lambda coord: coord.x_pos).x_pos
    min_x = min(coords, key=lambda coord: coord.x_pos).x_pos
    max_y = max(coords, key=lambda coord: coord.y_pos).y_pos
    min_y = min(coords, key=lambda coord: coord.y_pos).y_pos

    filas = max_x - min_x + 1
    columnas = max_y - min_y + 1

    matriz = np.zeros((6,6))
    for ficha in coords:
        x = ficha.x_pos
        y = ficha.y_pos
        matriz[x-1][y-1] = 1
    
    submatriz = matriz[min_x-1 : min_x-1 + filas, min_y-1 : min_y-1 + columnas]
    
    figure_rotations = generar_rotaciones(figure)

    for fig in figure_rotations:
        if np.array_equal(fig, submatriz):
            return True
        
    return False

class BlockManager:
    def __init__(self):
        self.games: Dict[int, Any] = {}
        
    def create_game(self, game_id: int) -> None:
        self.games[game_id] = {}
        
    def add_player(self, game_id: int, player_id: int) -> None:
        self.games[game_id][player_id] = {
            "is_blocked": False,
            "block_card_fig_id": 0,
            "other_cards_in_hand": []
            }

    def delete_player(self, game_id: int, player_id: int) -> None:
        print("delete_player")
        if game_id in self.games:
            if player_id in self.games[game_id]:
                del self.games[game_id][player_id]
        print("delete player worked")

    def delete_game(self, game_id: int) -> None:
        print("delete_game")
        if game_id in self.games:
            del self.games[game_id]
        print("delete game worked")
        
    def block_fig_card(self, game_id: int, player_blocked_id: int, block_fig_card_id: int, others_fig_cards_id: List[int] ):
        self.games[game_id][player_blocked_id]["is_blocked"] = True
        self.games[game_id][player_blocked_id]["block_card_fig_id"] = block_fig_card_id
        self.games[game_id][player_blocked_id]["other_cards_in_hand"] = others_fig_cards_id

    def is_blocked(self, game_id: int, player_id: int) -> bool:
        if game_id not in self.games:
            return False
        return self.games[game_id][player_id]["is_blocked"]
    
    def get_blocked_card_id(self, game_id: int, player_id: int) -> int:
        return self.games[game_id][player_id]["block_card_fig_id"]
    
    def delete_other_card(self, game_id: int, player_id: int, card_id: int) -> None:
        self.games[game_id][player_id]["other_cards_in_hand"].remove(card_id)

    def can_delete_blocked_card(self, game_id: int, player_id: int) -> bool:
        return len(self.games[game_id][player_id]["other_cards_in_hand"]) == 0

    def delete_blocked_card(self, game_id: int, player_id: int, block_card_id: int) -> None:

        if self.can_delete_blocked_card(game_id, player_id) == 0:
            if block_card_id == self.games[game_id][player_id]["block_card_fig_id"]:
                self.games[game_id][player_id]["is_blocked"] = False
                self.games[game_id][player_id]["block_card_fig_id"] = 0
                self.games[game_id][player_id]["other_cards_in_hand"] = []

    