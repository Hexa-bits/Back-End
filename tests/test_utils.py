import pytest

from unittest.mock import patch, MagicMock

from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.inputs_front import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard, Move
from src.models.fichas_cajon import FichaCajon
from src.utils_game import is_valid_move


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


    