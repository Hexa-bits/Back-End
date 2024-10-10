#Puede usarse tanto con una sola instancia de tablero e ir modificandola
#como tambien con dos instancias de tablero, una real y una parcial
#Esa decision se toma en ticket futuro, el GameManager sirve para ambos

class GameManager:
    def __init__(self):
        # Diccionario que guarda el estado de cada juego usando el game_id
        self.games = {}

    #Agregamos un nuevo juego al GameManager cuando se inicia la partida
    def create_game(self, game_id):
        # Crear una entrada para un nuevo juego con game_id
        self.games[game_id] = {
            'es_tablero_parcial': False,  # booleano que indica si el tablero usado es parcial o real
            'cartas_y_fichas_usadas': [],  # stack para apilar el carta_mov_id:int usada y par de coord(x,y) de fichas utilizadas ((x,y), (x,y))
                                            # e.g.: [(carta_mov_id, ((x,y),(x,y)), (carta_mov_id, ((x,y),(x,y)), ...]
            'jugador_en_turno_id': 0  # player_id:int del jugador en turno actual
        }

    #Eliminamos un juego del GameManager cuando se termina la partida (Alguien gana por abandono por ahora)
    def delete_game(self, game_id):
        # Eliminar el juego con game_id
        del self.games[game_id]

    '''''
    Estos metodos podemos obviarlos ya que seteamos el tablero parcial o real en base a otras acciones, no manualmente:
    def set_tablero_parcial(self, game_id) -> None:
        # Cambiar el tablero a parcial
        self.games[game_id]['es_tablero_parcial'] = True

    def set_tablero_real(self, game_id) -> None:
        # Cambiar el tablero a real
        self.games[game_id]['es_tablero_parcial'] = False
    '''

    #Sirve para saber si el tablero es parcial o real al enviar el tablero a Frontend
    def is_tablero_parcial(self, game_id) -> bool:
        # Obtener si el tablero es parcial
        return self.games[game_id]['es_tablero_parcial']

    #Apilar carta y par de fichas sirve para guardar cual fue el cambio parcial realizado
    #Siempre me convierte el tablero en parcial
    def apilar_carta_y_ficha(self, game_id, carta_mov_id, dupla_coords_ficha) -> None:
        # Apilar la carta usada y par de ficha utilizada en el stack
        self.games[game_id]['cartas_y_fichas_usadas'].append((carta_mov_id, dupla_coords_ficha))
        self.games[game_id]['is_tablero_parcial'] = True

    #Desapilar carta y par de fichas sirve para deshacer el cambio parcial realizado
    #Si el stack queda vacio, me convierte el tablero en real
    def desapilar_carta_y_ficha(self, game_id) -> tuple:
        # Desapilar la carta usada y par de ficha utilizada en el stack
        tupla_carta_fichas = self.games[game_id]['cartas_y_fichas_usadas'].pop()

        if self.games[game_id]['cartas_y_fichas_usadas'] == []:
            self.games[game_id]['is_tablero_parcial'] = False

        return tupla_carta_fichas

    #Limpiar cartas y fichas sirve para deshacernos del stack en caso de terminar turno o haber formado figura
    #Nos convierte el tablero en real
    def limpiar_cartas_fichas(self, game_id) -> None:
        # Limpiar el stack de cartas y fichas
        self.games[game_id]['cartas_y_fichas_usadas'] = []
        self.games[game_id]['is_tablero_parcial'] = False

    #ESTO NO LO USARIAMOS PORQUE APILAMOS Y DESAPILAMOS, PERO A FUTURO PUEDE SER UTIL
    #def obtener_cartas_fichas(self, game_id):
    #    # Obtener el stack de cartas y fichas
    #    return self.games[game_id]['cartas_y_fichas_usadas']

    #Sirve para saber que a que jugador devolverle la carta en caso de cancelar mov parcial
    def obtener_jugador_en_turno_id(self, game_id) -> int:
        # Obtener el jugador en turno
        return self.games[game_id]['jugador_en_turno_id']

    def set_jugador_en_turno_id(self, game_id, jugador_id):
        # Cambiar el jugador en turno
        self.games[game_id]['jugador_en_turno_id'] = jugador_id
