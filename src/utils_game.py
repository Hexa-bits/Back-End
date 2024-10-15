from src.models.events import Event
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.inputs_front import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard, Move
from src.models.fichas_cajon import FichaCajon
from typing import List, Tuple
import pdb

def is_valid_move(movementCard: MovementCard, coords: List[Tuple[int, int]]) -> bool:
    
    distancia_x = abs(coords[0][0]-coords[1][0])
    distancia_y = abs(coords[0][1]-coords[1][1])

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
                (coords[0][0]==1 or coords[1][0]==1 or coords[0][0]==6 or coords[1][0]==6)) #Alguna de las fichas tiene que estar
                or                                                                          #en los extremos
                (1 <= distancia_y <= 5 and distancia_x == 0 and
                (coords[0][1]==1 or coords[1][1]==1 or coords[0][1]==6 or coords[1][1]==6))) #Idem
    
    else:
        max_x_tuple = max(coords, key=lambda coord: coord[0])       #
        min_x_tuple = min(coords, key=lambda coord: coord[0])       #Para poder diferenciar los movimientos L

        distancia_entre_fichas_ejeY = max_x_tuple[1]-min_x_tuple[1]
        
        if movementCard.movimiento == Move.L_derecha:
            return ( ((distancia_y == 1 and distancia_x == 2) and (distancia_entre_fichas_ejeY>0)) #<-- Desde la perspectiva de la 
                    or ((distancia_y == 2 and distancia_x == 1) and distancia_entre_fichas_ejeY<0) )    #ficha de mas abajo del tablero
                                                                                                        #es como que "volves"
                                                                                                        #en columna
        elif movementCard.movimiento == Move.L_izquierda:
            return ( ((distancia_y == 1 and distancia_x == 2) and (distancia_entre_fichas_ejeY<0)) #<-- Idem pero al contrario
                    or ((distancia_y == 2 and distancia_x == 1) and distancia_entre_fichas_ejeY>0) )   #es como que "vas para adelante" 
                
                 
    return False
