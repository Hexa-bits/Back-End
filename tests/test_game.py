import numpy as np
import pytest
from src.game import detectar_patrones, figura_valida, separar_matrices_por_color

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

if __name__ == "__main__":
    pytest.main()
