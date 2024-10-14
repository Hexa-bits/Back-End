from typing import List, Dict, Any

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

    def create_game(self, game_id) -> None:
        """Agregamos un nuevo juego al GameManager cuando se inicia la partida"""
        
        # Crear una entrada para un nuevo juego con game_id
        self.games[game_id] = {
            'es_tablero_parcial': False,  # booleano que indica si el tablero usado es parcial o real
            'cartas_y_fichas_usadas': [],  # stack para apilar el carta_mov_id:int usada y par de coord(x,y) de fichas utilizadas ((x,y), (x,y))
                                            # e.g.: [(carta_mov_id, ((x,y),(x,y)), (carta_mov_id, ((x,y),(x,y)), ...]
            'jugador_en_turno_id': 0  # player_id:int del jugador en turno actual
        }

    def delete_game(self, game_id) -> None:
        """Eliminamos un juego del GameManager cuando se termina la partida (Alguien gana por abandono por ahora)"""
        
        # Eliminar el juego con game_id
        del self.games[game_id]


    def is_tablero_parcial(self, game_id) -> bool:
        """Sirve para saber si el tablero es parcial o real al enviar el tablero a Frontend"""
        
        # Obtener si el tablero es parcial
        return self.games[game_id]['es_tablero_parcial']


    def apilar_carta_y_ficha(self, game_id, carta_mov_id, dupla_coords_ficha) -> None:
        """
        Apilar carta y par de fichas sirve para guardar cual fue el cambio parcial realizado
        Siempre me convierte el tablero en parcial
        """
        # Apilar la carta usada y par de ficha utilizada en el stack
        self.games[game_id]['cartas_y_fichas_usadas'].append((carta_mov_id, dupla_coords_ficha))
        self.games[game_id]['es_tablero_parcial'] = True

    def desapilar_carta_y_ficha(self, game_id) -> tuple:
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

    def limpiar_cartas_fichas(self, game_id) -> None:
        """
        Limpiar cartas y fichas sirve para deshacernos del stack en caso haber formado figura
        Nos convierte el tablero en real
        """
        # Limpiar el stack de cartas y fichas
        self.games[game_id]['cartas_y_fichas_usadas'] = []
        self.games[game_id]['es_tablero_parcial'] = False

    def obtener_jugador_en_turno_id(self, game_id) -> int:
        """
        Obtener el jugador en turno
        Sirve para saber que a que jugador devolverle la carta en caso de cancelar mov parcial
        """

        return self.games[game_id]['jugador_en_turno_id']

    def set_jugador_en_turno_id(self, game_id, jugador_id) -> None:
        """Cambiar el jugador en turno"""
        self.games[game_id]['jugador_en_turno_id'] = jugador_id
