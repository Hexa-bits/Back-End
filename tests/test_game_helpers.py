from unittest.mock import patch, MagicMock
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.cartamovimiento import MovementCard, Move
from src.models.fichas_cajon import FichaCajon
from src.models.utils import *
from src.game_helpers import *
    
def test_create_game():
    """Pruebo si el juego se crea correctamente."""
    game_manager = GameManager()
    game_id = 1
    game_manager.create_game(game_id)
    assert game_id in game_manager.games
    assert game_manager.games[game_id]['es_tablero_parcial'] == False
    assert game_manager.games[game_id]['cartas_y_fichas_usadas'] == []
    assert game_manager.games[game_id]['jugador_en_turno_id'] == 0

def test_delete_game():
    """Pruebo si el juego se elimina correctamente."""
    game_manager = GameManager()
    game_id = 1
    game_manager.create_game(game_id)
    game_manager.delete_game(game_id)
    assert game_id not in game_manager.games

def test_apilar_carta_y_ficha():
    """Pruebo si apilar una carta y fichas convierte el tablero en parcial."""
    game_manager = GameManager()
    game_id = 1
    coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))
    game_manager.create_game(game_id)
    game_manager.apilar_carta_y_ficha(game_id, 1, coords)

    # Verificamos que la carta y fichas fueron apiladas
    assert game_manager.games[game_id]['cartas_y_fichas_usadas'] == [(1, coords)]
    # Verificamos que el tablero se convirtió en parcial
    assert game_manager.games[game_id]['es_tablero_parcial'] == True

def test_desapilar_carta_y_ficha():
    """Pruebo si desapilar una carta y fichas convierte el tablero en real si el stack está vacío."""
    game_manager = GameManager()
    game_id = 1
    game_manager.create_game(game_id)
    game_manager.apilar_carta_y_ficha(game_id, 1, ((0, 0), (1, 1)))
    carta_ficha = game_manager.desapilar_carta_y_ficha(game_id)

    # Verificamos que se haya desapilado correctamente
    assert carta_ficha == (1, ((0, 0), (1, 1)))
    # Verificamos que el stack está vacío y el tablero es real
    assert game_manager.games[game_id]['cartas_y_fichas_usadas'] == []
    assert game_manager.games[game_id]['es_tablero_parcial'] == False

def test_limpiar_cartas_fichas():
    """Pruebo si limpiar el stack convierte el tablero en real."""
    game_manager = GameManager()
    game_id = 1
    coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))
    game_manager.create_game(game_id)
    game_manager.apilar_carta_y_ficha(game_id, 1, coords)
    game_manager.limpiar_cartas_fichas(game_id)

    # Verificamos que el stack esté vacío y el tablero sea real
    assert game_manager.games[game_id]['cartas_y_fichas_usadas'] == []
    assert game_manager.games[game_id]['es_tablero_parcial'] == False

def test_top_tupla_carta_y_fichas():
    """Pruebo si obtengo el último par (id movimiento, coordenadas cajon)"""
    game_manager = GameManager()
    game_id = 1
    coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))
    game_manager.create_game(game_id)
    game_manager.apilar_carta_y_ficha(game_id, 1, coords)
    ultimo_parcial = game_manager.top_tupla_carta_y_fichas(game_id)

    assert ultimo_parcial == (1, coords)

def test_jugador_en_turno():
    """Pruebo si se obtiene y cambia el jugador en turno correctamente."""
    game_manager = GameManager()
    game_id = 1
    game_manager.create_game(game_id)
    game_manager.set_jugador_en_turno_id(game_id, 42)

    # Verificamos que el jugador en turno sea el correcto
    assert game_manager.obtener_jugador_en_turno_id(game_id) == 42

def test_valid_mov():
    mock_line_to_side_card = MagicMock()
    mock_right_L_card = MagicMock()
    mock_left_L_card = MagicMock()

    mock_line_to_side_card.return_value = MovementCard(movimiento = Move.linea_al_lateral)
    mock_right_L_card.return_value = MovementCard(movimiento = Move.L_derecha)
    mock_left_L_card.return_value = MovementCard(movimiento = Move.L_izquierda)

    assert False == is_valid_move(mock_line_to_side_card.return_value, (Coords(x_pos=2, y_pos=1), Coords(x_pos=3, y_pos=1)))
    assert False == is_valid_move(mock_line_to_side_card.return_value, (Coords(x_pos=2, y_pos=2), Coords(x_pos=2, y_pos=5)))
    assert False == is_valid_move(mock_line_to_side_card.return_value, (Coords(x_pos=2, y_pos=1), Coords(x_pos=3, y_pos=2)))

    assert True == is_valid_move(mock_line_to_side_card.return_value, (Coords(x_pos=2, y_pos=2), Coords(x_pos=2, y_pos=6)))
    assert True == is_valid_move(mock_line_to_side_card.return_value, (Coords(x_pos=5, y_pos=1), Coords(x_pos=6, y_pos=1)))
    assert True == is_valid_move(mock_line_to_side_card.return_value, (Coords(x_pos=1, y_pos=1), Coords(x_pos=1, y_pos=6)))

    ficha3_3 = Coords(x_pos=3, y_pos=3)
    ficha4_1 = Coords(x_pos=4, y_pos=1)
    assert False == is_valid_move(mock_left_L_card.return_value, (ficha3_3, ficha4_1))
    assert True == is_valid_move(mock_right_L_card.return_value, (ficha3_3, ficha4_1))

    ficha5_4 = Coords(x_pos=5, y_pos=4)
    assert False == is_valid_move(mock_left_L_card.return_value, (ficha3_3, ficha5_4))
    assert True == is_valid_move(mock_right_L_card.return_value, (ficha3_3, ficha5_4))
    
    ficha3_5 = Coords(x_pos=3, y_pos=5)
    ficha1_6 = Coords(x_pos=1, y_pos=6)
    assert False == is_valid_move(mock_right_L_card.return_value, (ficha3_5, ficha1_6))
    assert True == is_valid_move(mock_left_L_card.return_value, (ficha3_5, ficha1_6))

    ficha5_6 = Coords(x_pos=5, y_pos=6)
    ficha4_4 = Coords(x_pos=4, y_pos=4)
    assert False == is_valid_move(mock_right_L_card.return_value, (ficha5_6, ficha4_4))
    assert True == is_valid_move(mock_left_L_card.return_value, (ficha5_6, ficha4_4))

    assert False == is_valid_move(mock_right_L_card.return_value, (ficha3_3, Coords(x_pos=2, y_pos=2)))
    assert False == is_valid_move(mock_left_L_card.return_value, (ficha3_3, Coords(x_pos=3, y_pos=2)))

def test_detectar_patrones_sin_patrones():
    matriz = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    patrones = [np.array([[1, 1], [1, 1]])]
    assert detectar_patrones(matriz, patrones) == []

def test_detectar_patrones_con_patrones():
    matriz = np.array([[1, 1, 0], [1, 1, 0], [0, 0, 0]])
    patrones = [np.array([[1, 1], [1, 1]])]
    resultado_esperado = [[(0, 0), (0, 1), (1, 0), (1, 1)]]
    assert detectar_patrones(matriz, patrones) == resultado_esperado

def test_detectar_varios_patrones():
    matriz = np.array([[1, 1, 1], [1, 1, 1], [0, 1, 1]])
    patrones = [np.array([[1, 1], [1, 1]])]
    resultado_esperado = [
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(1, 1), (1, 2), (2, 1), (2, 2)]
    ]
    assert detectar_patrones(matriz, patrones) == resultado_esperado

def test_figura_valida_true():
    matriz = np.array([[1, 0], [0, 1]])
    coords_validas = [(0, 0), (1, 1)]
    assert figura_valida(matriz, coords_validas) is True

def test_figura_valida_false():
    matriz = np.array([[1, 1], [1, 0]])
    coords_validas = [(0, 0), (1, 0)]
    assert figura_valida(matriz, coords_validas) is False  # Tiene un vecino adyacente

def test_separar_matrices_por_color():
    matriz = np.array([[1, 2], [2, 1]])
    lista_colores = [1, 2]
    resultado_esperado = [
        np.array([[1, 0], [0, 1]]),  # Matriz de color 1
        np.array([[0, 1], [1, 0]])   # Matriz de color 2
    ]
    matrices_resultantes = separar_matrices_por_color(matriz, lista_colores)
    for result, esperado in zip(matrices_resultantes, resultado_esperado):
        assert np.array_equal(result, esperado)

def test_separar_matrices_por_color_sin_color():
    matriz = np.array([[0, 0], [0, 0]])
    lista_colores = [1]
    resultado_esperado = [np.zeros((2, 2))]
    matrices_resultantes = separar_matrices_por_color(matriz, lista_colores)
    assert np.array_equal(matrices_resultantes[0], resultado_esperado[0])

def test_is_valid_picture_card():
    cartaFigura = MagicMock()
    cartaFigura.return_value = PictureCard(figura= Picture.figura12)

    coords = [Coords(x_pos= 2, y_pos= 2), Coords(x_pos= 3, y_pos= 2), Coords(x_pos= 3, y_pos= 3), 
              Coords(x_pos= 3, y_pos= 4), Coords(x_pos= 4, y_pos= 4)]

    assert is_valid_picture_card(cartaFigura.return_value, coords) == True

    cartaFigura.return_value = PictureCard(figura= Picture.figura10)

    coords = [Coords(x_pos= 1, y_pos= 6), Coords(x_pos= 2, y_pos= 6), Coords(x_pos= 2, y_pos= 5), 
              Coords(x_pos= 2, y_pos= 4), Coords(x_pos= 3, y_pos= 4)]
    
    assert is_valid_picture_card(cartaFigura.return_value, coords)

    cartaFigura.return_value = PictureCard(figura= Picture.figura10)

    coords = [Coords(x_pos= 4, y_pos= 4), Coords(x_pos= 4, y_pos= 5), Coords(x_pos= 5, y_pos= 5),      #Figura 10 rotada 1 vez 
              Coords(x_pos= 6, y_pos= 5), Coords(x_pos= 6, y_pos= 6)]
    
    assert is_valid_picture_card(cartaFigura.return_value, coords)

    cartaFigura.return_value = PictureCard(figura= Picture.figura14)

    coords = [Coords(x_pos= 4, y_pos= 5), Coords(x_pos= 5, y_pos= 3), Coords(x_pos= 5, y_pos= 4),      #Figura 14 rotada 2 veces 
              Coords(x_pos= 5, y_pos= 5), Coords(x_pos= 5, y_pos= 6)]
    
    assert is_valid_picture_card(cartaFigura.return_value, coords)

    coords = [Coords(x_pos= 1, y_pos= 6), Coords(x_pos= 2, y_pos= 6), Coords(x_pos= 2, y_pos= 5),      #Figura 10 con carta
              Coords(x_pos= 2, y_pos= 4), Coords(x_pos= 3, y_pos= 4)]                                 #Figura 14
    
    assert not is_valid_picture_card(cartaFigura.return_value, coords)

    coords = [Coords(x_pos= 4, y_pos= 4), Coords(x_pos= 4, y_pos= 5), Coords(x_pos= 5, y_pos= 5),      #Figura 10 rotada 1 vez 
              Coords(x_pos= 6, y_pos= 5), Coords(x_pos= 6, y_pos= 6)]                                 #con carta Figura 14
 
    assert not is_valid_picture_card(cartaFigura.return_value, coords)