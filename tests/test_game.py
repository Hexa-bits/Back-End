import numpy as np
import pytest
from unittest.mock import MagicMock 
from src.models.partida import Partida
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.inputs_front import Ficha
from typing import List
from src.game import detectar_patrones, figura_valida, separar_matrices_por_color, is_valid_picture_card

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

    fichas = [Ficha(x_pos= 2, y_pos= 2), Ficha(x_pos= 3, y_pos= 2), Ficha(x_pos= 3, y_pos= 3), 
              Ficha(x_pos= 3, y_pos= 4), Ficha(x_pos= 4, y_pos= 4)]

    assert is_valid_picture_card(cartaFigura.return_value, fichas) == True

    cartaFigura.return_value = PictureCard(figura= Picture.figura10)

    fichas = [Ficha(x_pos= 1, y_pos= 6), Ficha(x_pos= 2, y_pos= 6), Ficha(x_pos= 2, y_pos= 5), 
              Ficha(x_pos= 2, y_pos= 4), Ficha(x_pos= 3, y_pos= 4)]
    
    assert is_valid_picture_card(cartaFigura.return_value, fichas)

    cartaFigura.return_value = PictureCard(figura= Picture.figura10)

    fichas = [Ficha(x_pos= 4, y_pos= 4), Ficha(x_pos= 4, y_pos= 5), Ficha(x_pos= 5, y_pos= 5),      #Figura 10 rotada 1 vez 
              Ficha(x_pos= 6, y_pos= 5), Ficha(x_pos= 6, y_pos= 6)]
    
    assert is_valid_picture_card(cartaFigura.return_value, fichas)

    cartaFigura.return_value = PictureCard(figura= Picture.figura14)

    fichas = [Ficha(x_pos= 4, y_pos= 5), Ficha(x_pos= 5, y_pos= 3), Ficha(x_pos= 5, y_pos= 4),      #Figura 14 rotada 2 veces 
              Ficha(x_pos= 5, y_pos= 5), Ficha(x_pos= 5, y_pos= 6)]
    
    assert is_valid_picture_card(cartaFigura.return_value, fichas)

    fichas = [Ficha(x_pos= 1, y_pos= 6), Ficha(x_pos= 2, y_pos= 6), Ficha(x_pos= 2, y_pos= 5),      #Figura 10 con carta
              Ficha(x_pos= 2, y_pos= 4), Ficha(x_pos= 3, y_pos= 4)]                                 #Figura 14
    
    assert ~is_valid_picture_card(cartaFigura.return_value, fichas)

    fichas = [Ficha(x_pos= 4, y_pos= 4), Ficha(x_pos= 4, y_pos= 5), Ficha(x_pos= 5, y_pos= 5),      #Figura 10 rotada 1 vez 
              Ficha(x_pos= 6, y_pos= 5), Ficha(x_pos= 6, y_pos= 6)]                                 #con carta Figura 14
 
    assert ~is_valid_picture_card(cartaFigura.return_value, fichas)

if __name__ == "__main__":
    pytest.main()
