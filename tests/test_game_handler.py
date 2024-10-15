from unittest.mock import patch, MagicMock

from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard, Move
from src.models.fichas_cajon import FichaCajon
from src.game import GameManager, is_valid_move
    
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
    game_manager.create_game(game_id)
    game_manager.apilar_carta_y_ficha(game_id, 1, ((0, 0), (1, 1)))

    # Verificamos que la carta y fichas fueron apiladas
    assert game_manager.games[game_id]['cartas_y_fichas_usadas'] == [(1, ((0, 0), (1, 1)))]
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
    game_manager.create_game(game_id)
    game_manager.apilar_carta_y_ficha(game_id, 1, ((0, 0), (1, 1)))
    game_manager.limpiar_cartas_fichas(game_id)

    # Verificamos que el stack esté vacío y el tablero sea real
    assert game_manager.games[game_id]['cartas_y_fichas_usadas'] == []
    assert game_manager.games[game_id]['es_tablero_parcial'] == False

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

    assert False == is_valid_move(mock_line_to_side_card.return_value, [(2,1), (3,1)])
    assert False == is_valid_move(mock_line_to_side_card.return_value, [(2,2), (2,5)])
    assert False == is_valid_move(mock_line_to_side_card.return_value, [(2,1), (3,2)])

    assert True == is_valid_move(mock_line_to_side_card.return_value, [(2,2), (2,6)])
    assert True == is_valid_move(mock_line_to_side_card.return_value, [(5,1), (6,1)])
    assert True == is_valid_move(mock_line_to_side_card.return_value, [(1,1), (1,6)])

    assert False == is_valid_move(mock_left_L_card.return_value, [(3,3), (4,1)])
    assert True == is_valid_move(mock_right_L_card.return_value, [(3,3), (4,1)])

    assert False == is_valid_move(mock_left_L_card.return_value, [(3,3), (5,4)])
    assert True == is_valid_move(mock_right_L_card.return_value, [(3,3), (5,4)])

    assert False == is_valid_move(mock_left_L_card.return_value, [(3,3), (3,2)])
    
    assert False == is_valid_move(mock_right_L_card.return_value, [(3,5), (1,6)])
    assert True == is_valid_move(mock_left_L_card.return_value, [(3,5), (1,6)])

    assert False == is_valid_move(mock_right_L_card.return_value, [(5,6), (4,4)])
    assert True == is_valid_move(mock_left_L_card.return_value, [(5,6), (4,4)])

    assert False == is_valid_move(mock_right_L_card.return_value, [(3,3), (2,2)])


    