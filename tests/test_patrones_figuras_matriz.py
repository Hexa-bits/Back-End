import pytest
import numpy as np
from src.models.patrones_figuras_matriz import generar_rotaciones, generate_all_figures

def test_generar_rotaciones():
    # Patrón base para rotar
    patron = np.array([
        [1, 0],
        [0, 1]
    ])

    # Llamada a la función
    rotaciones = generar_rotaciones(patron)

    # Verificamos que las 4 rotaciones son distintas
    assert len(rotaciones) == 4

    # Rotación original
    assert np.array_equal(rotaciones[0], patron)

    # Rotación 90 grados
    assert np.array_equal(rotaciones[1], np.array([
        [0, 1],
        [1, 0]
    ]))

    # Rotación 180 grados
    assert np.array_equal(rotaciones[2], np.array([
        [1, 0],
        [0, 1]
    ]))

    # Rotación 270 grados
    assert np.array_equal(rotaciones[3], np.array([
        [0, 1],
        [1, 0]
    ]))

def test_generate_all_figures():
    # Llamada a la función
    all_figures = generate_all_figures()

    # Verificamos que se generen exactamente 100 figuras (25 figuras originales * 4 rotaciones)
    assert len(all_figures) == 100

if __name__ == "__main__":
    pytest.main()
