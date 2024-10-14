import numpy as np

def detectar_patrones(matriz, patrones) -> list:
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
                # Si el vecino es un 1 y no está en la lista de coordenadas válidas
                if matriz[nx, ny] == 1 and (nx, ny) not in coordenadas_set:
                    return False  # Hay un 1 no válido adyacente
    return True  # Todos los vecinos son válidos

def separar_matrices_por_color(matriz, lista_colores) -> list:
    """Separa la matriz de colores en matrices individuales por color.
    Toma como elementos:
    matriz: Una matriz numpy donde cada elemento representa un color.
    lista_colores: Una lista de colores presentes en la matriz.
    
    Devuelve una lista de matrices, donde cada matriz representa un color.
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
        self.games = {}

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
        self.games[game_id]['is_tablero_parcial'] = True

    def desapilar_carta_y_ficha(self, game_id) -> tuple:
        """
        Desapilar carta y par de fichas sirve para deshacer el cambio parcial realizado
        Si el stack queda vacio, me convierte el tablero en real
        Si termina el turno y no se formó figura, se debe desapilar, revertir el movimiento de fichas y devolver la carta_mov al jugador
        Hasta que el stack quede vacio, osea, hasta que el tablero sea real
        Desapilar la carta usada y par de ficha utilizada en el stack
        """

        tupla_carta_fichas = None

        if self.games[game_id]['is_tablero_parcial']:
            tupla_carta_fichas = self.games[game_id]['cartas_y_fichas_usadas'].pop()
            
            if self.games[game_id]['cartas_y_fichas_usadas'] == []:
                self.games[game_id]['is_tablero_parcial'] = False

        return tupla_carta_fichas

    def limpiar_cartas_fichas(self, game_id) -> None:
        """
        Limpiar cartas y fichas sirve para deshacernos del stack en caso haber formado figura
        Nos convierte el tablero en real
        """
        # Limpiar el stack de cartas y fichas
        self.games[game_id]['cartas_y_fichas_usadas'] = []
        self.games[game_id]['is_tablero_parcial'] = False

    def obtener_jugador_en_turno_id(self, game_id) -> int:
        """
        Obtener el jugador en turno
        Sirve para saber que a que jugador devolverle la carta en caso de cancelar mov parcial
        """

        return self.games[game_id]['jugador_en_turno_id']

    def set_jugador_en_turno_id(self, game_id, jugador_id) -> None:
        """Cambiar el jugador en turno"""
        self.games[game_id]['jugador_en_turno_id'] = jugador_id