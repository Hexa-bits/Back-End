class GameManager:
    def __init__(self):
        # Diccionario que guarda el estado de cada juego usando el game_id
        self.games = {}

    def create_game(self, game_id, jugador_turno):
        # Crear una entrada para un nuevo juego con game_id
        self.games[game_id] = {
            'es_tablero_parcial': False,  # booleano que indica si el tablero usado es parcial o real
            'cartas_y_fichas_usadas': [],  # stack para apilar id de carta_mov usada y par de coord(x,y) de ficha utilizada ((x,y), (x,y))
            'jugador_turno': jugador_turno  # player_id del jugador en turno actual
        }

    def delete_game(self, game_id):
        # Eliminar el juego con game_id
        del self.games[game_id]

    '''''
    Estos metodos podemos obviarlos ya que seteamos el tablero parcial o real en base a otras acciones:
    def set_tablero_parcial(self, game_id) -> None:
        # Cambiar el tablero a parcial
        self.games[game_id]['es_tablero_parcial'] = True

    def set_tablero_real(self, game_id) -> None:
        # Cambiar el tablero a real
        self.games[game_id]['es_tablero_parcial'] = False
    '''
    
    def is_tablero_parcial(self, game_id) -> bool:
        # Obtener si el tablero es parcial
        return self.games[game_id]['es_tablero_parcial']

    def apilar_carta_y_ficha(self, game_id, carta, coord_dupla_ficha) -> None:
        # Apilar la carta usada y par de ficha utilizada en el stack
        self.games[game_id]['cartas_y_fichas_usadas'].append((carta, coord_dupla_ficha))
        self.games[game_id]['is_tablero_parcial'] = True

    def desapilar_carta_y_ficha(self, game_id, carta, coord_dupla_ficha) -> tuple:
        # Apilar la carta usada y par de ficha utilizada en el stack
        tupla_carta_fichas = self.games[game_id]['cartas_y_fichas_usadas'].pop((carta, coord_dupla_ficha))

        if self.games[game_id]['cartas_y_fichas_usadas'] == []:
            self.games[game_id]['is_tablero_parcial'] = False

        return tupla_carta_fichas

    def limpiar_cartas_fichas(self, game_id) -> None:
        # Limpiar el stack de cartas y fichas
        self.games[game_id]['cartas_y_fichas_usadas'] = []
        self.games[game_id]['is_tablero_parcial'] = False

    #ESTO NO LO USARIAMOS PORQUE APILAMOS Y DESAPILAMOS
    #def obtener_cartas_fichas(self, game_id):
    #    # Obtener el stack de cartas y fichas
    #    return self.games[game_id]['cartas_y_fichas_usadas']

    def obtener_jugador_en_turno_id(self, game_id) -> int:
        # Obtener el jugador en turno
        return self.games[game_id]['jugador_turno']

    def set_jugador_en_turno_id(self, game_id, jugador_turno):
        # Cambiar el jugador en turno
        self.games[game_id]['jugador_turno'] = jugador_turno
