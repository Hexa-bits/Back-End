import numpy as np
import pytest
from unittest.mock import MagicMock 
from src.models.partida import Partida
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.utils import Coords
from typing import List
from src.game import BlockManager, detectar_patrones, figura_valida, separar_matrices_por_color, is_valid_picture_card

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


@pytest.fixture
def block_manager():
    return BlockManager()

def test_create_game(block_manager):
    block_manager.create_game(1)
    assert 1 in block_manager.games

def test_add_player(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    assert 101 in block_manager.games[1]
    assert block_manager.games[1][101]["is_blocked"] is False
    assert block_manager.games[1][101]["block_card_fig_id"] == 0
    assert block_manager.games[1][101]["other_cards_in_hand"] == []

def test_delete_player(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.delete_player(1, 101)
    assert 101 not in block_manager.games[1]

def test_delete_game(block_manager):
    block_manager.create_game(1)
    block_manager.delete_game(1)
    assert 1 not in block_manager.games

def test_block_fig_card(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [3, 7, 9])
    assert block_manager.games[1][101]["is_blocked"] is True
    assert block_manager.games[1][101]["block_card_fig_id"] == 5
    assert block_manager.games[1][101]["other_cards_in_hand"] == [3, 7, 9]

def test_is_blocked(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    assert block_manager.is_blocked(1, 101) is False
    block_manager.block_fig_card(1, 101, 5, [3, 7, 9])
    assert block_manager.is_blocked(1, 101) is True

def test_get_blocked_card_id(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [3, 7, 9])
    assert block_manager.get_blocked_card_id(1, 101) == 5

def test_delete_other_card(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [3, 7, 9])
    block_manager.delete_other_card(1, 101, 7)
    assert block_manager.games[1][101]["other_cards_in_hand"] == [3, 9]

def test_can_delete_blocked_card(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [])
    assert block_manager.can_delete_blocked_card(1, 101) is True

def test_delete_blocked_card(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [])
    block_manager.delete_blocked_card(1, 101, 5)
    assert block_manager.games[1][101]["is_blocked"] is False
    assert block_manager.games[1][101]["block_card_fig_id"] == 0
    assert block_manager.games[1][101]["other_cards_in_hand"] == []

# Testeo el block_manager

@pytest.fixture
def block_manager():
    return BlockManager()

def test_create_game(block_manager):
    block_manager.create_game(1)
    assert 1 in block_manager.games

def test_add_player(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    assert 101 in block_manager.games[1]
    assert block_manager.games[1][101]["is_blocked"] is False
    assert block_manager.games[1][101]["block_card_fig_id"] == 0
    assert block_manager.games[1][101]["other_cards_in_hand"] == []

def test_delete_player(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.delete_player(1, 101)
    assert 101 not in block_manager.games[1]

def test_delete_game(block_manager):
    block_manager.create_game(1)
    block_manager.delete_game(1)
    assert 1 not in block_manager.games

def test_block_fig_card(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [3, 7, 9])
    assert block_manager.games[1][101]["is_blocked"] is True
    assert block_manager.games[1][101]["block_card_fig_id"] == 5
    assert block_manager.games[1][101]["other_cards_in_hand"] == [3, 7, 9]

def test_is_blocked(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    assert block_manager.is_blocked(1, 101) is False
    block_manager.block_fig_card(1, 101, 5, [3, 7, 9])
    assert block_manager.is_blocked(1, 101) is True

def test_get_blocked_card_id(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [3, 7])
    assert block_manager.get_blocked_card_id(1, 101) == 5

def test_delete_other_card(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [3, 7])
    block_manager.delete_other_card(1, 101, 7)
    assert block_manager.games[1][101]["other_cards_in_hand"] == [3]
    block_manager.delete_other_card(1, 101, 3)
    assert block_manager.games[1][101]["other_cards_in_hand"] == []

def test_can_delete_blocked_card(block_manager):
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [4,8])
    assert block_manager.can_delete_blocked_card(1, 101) is False
    block_manager.delete_other_card(1, 101, 4)
    assert block_manager.can_delete_blocked_card(1, 101) is False
    block_manager.delete_other_card(1, 101, 8)
    assert block_manager.can_delete_blocked_card(1, 101) is True

def test_delete_blocked_card(block_manager):
    #Solo puedo borrar la carta bloqueada si no tengo otras cartas en la mano, esto me desbloquea al jugador
    block_manager.create_game(1)
    block_manager.add_player(1, 101)
    block_manager.block_fig_card(1, 101, 5, [8,11])
    delete = block_manager.delete_blocked_card(1, 101, 5)
    assert delete is False
    block_manager.delete_other_card(1, 101, 8)
    delete = block_manager.delete_blocked_card(1, 101, 5)
    assert delete is False
    block_manager.delete_other_card(1, 101, 11)
    delete = block_manager.delete_blocked_card(1, 101, 5)
    assert delete is True
    assert block_manager.games[1][101]["is_blocked"] is False
    assert block_manager.games[1][101]["block_card_fig_id"] == 0
    assert block_manager.games[1][101]["other_cards_in_hand"] == []

