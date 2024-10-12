from src.models.events import Event
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.inputs_front import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard, Move
from src.models.fichas_cajon import FichaCajon
from typing import List, Tuple


def is_valid_move(movementCard: MovementCard, coords: List[Tuple[int, int]]) -> bool:
    max_x_tuple = max(coords, key=lambda coord: coord[0])       #
    min_x_tuple = min(coords, key=lambda coord: coord[0])       #Para poder diferenciar los movimientos L
    
    distancia_x = max_x_tuple[0]-min_x_tuple[0]
    distancia_entre_fichas_ejeY = max_x_tuple[1]-min_x_tuple[1]

    distancia_y = abs(distancia_entre_fichas_ejeY)

    if movementCard.movimiento == Move.linea_contiguo:
        return (distancia_y == 0 and distancia_x == 1) or (distancia_y == 1 and distancia_x == 0)
    
    elif movementCard.movimiento == Move.linea_con_espacio:
        return (distancia_y == 0 and distancia_x == 2) or (distancia_y == 2 and distancia_x == 0)
    
    elif movementCard.movimiento == Move.diagonal_contiguo:
        return distancia_y == 1 and distancia_x == 1
    
    elif movementCard.movimiento == Move.diagonal_con_espacio:
        return distancia_y == 2 and distancia_x == 2
    
    elif movementCard.movimiento in Move.L_derecha:
        return ( ((distancia_y == 1 and distancia_x == 2) and (distancia_entre_fichas_ejeY>0))      #Desde la perspectiva de la 
                or ((distancia_y == 2 and distancia_x == 1) and distancia_entre_fichas_ejeY<0) )    #ficha de mas abajo del tablero
                                                                                                    #es como que "volves"
                                                                                                    #en columna
    elif movementCard.movimiento in Move.L_izquierda:
        return ( ((distancia_y == 1 and distancia_x == 2) and (distancia_entre_fichas_ejeY<0))     #Idem pero al contrario
                or ((distancia_y == 2 and distancia_x == 1) and distancia_entre_fichas_ejeY>0) )   #es como que "vas para adelante"
    
    elif movementCard.movimiento == Move.linea_al_lateral:
        return (distancia_y == 0 and 1 <= distancia_x <= 5) or (1 <= distancia_y <= 5 and distancia_x == 0)
    
    return False
