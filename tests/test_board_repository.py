import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from src.repositories.board_repository import get_valid_detected_figures, get_color_of_ficha
from src.models.fichas_cajon import FichaCajon, Color  # Ajustar importación según tu estructura
import numpy as np

# Mock de la función get_fichas
def mock_get_fichas(game_id, db):
    return [
        {"x": 1, "y": 1, "color": Color.ROJO},
        {"x": 1, "y": 2, "color": Color.VERDE},
        {"x": 1, "y": 3, "color": Color.VERDE},
        {"x": 2, "y": 1, "color": Color.ROJO},
        {"x": 2, "y": 2, "color": Color.VERDE},
        {"x": 2, "y": 3, "color": Color.ROJO},
        {"x": 3, "y": 1, "color": Color.ROJO},
        {"x": 3, "y": 2, "color": Color.ROJO},
        {"x": 3, "y": 3, "color": Color.AZUL}
    ]

# Mock de la función get_tablero
def mock_get_tablero(game_id, db):
    return Mock(id=1)  # Retorna un objeto con un id de tablero

@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

def test_get_valid_detected_figures(mock_db_session, monkeypatch):
    # Mockear get_fichas para simular la base de datos
    monkeypatch.setattr('src.repositories.board_repository.get_fichas', mock_get_fichas)
    
    # Patrón que será detectado
    lista_patrones = [np.array([[1, 1], [1, 0]])]

    # Llamada a la función
    figuras_validas = get_valid_detected_figures(game_id=1, lista_patrones=lista_patrones, db=mock_db_session)

    # Verificar que se detectó la figura válida
    assert figuras_validas == [[(0, 1), (0,2), (1, 1)]]  # De acuerdo a las coordenadas de mock_get_fichas

def test_get_valid_detected_figures_sin_figuras(mock_db_session, monkeypatch):
    # Mockear get_fichas para devolver un tablero vacío
    monkeypatch.setattr('src.repositories.board_repository.get_fichas', lambda game_id, db: [])
    
    # Patrón que será detectado
    lista_patrones = [np.array([[1, 0], [0, 1]])]

    # Llamada a la función
    figuras_validas = get_valid_detected_figures(game_id=1, lista_patrones=lista_patrones, db=mock_db_session)

    # Verificar que no se detectan figuras
    assert figuras_validas == []

def test_get_color_of_ficha(mock_db_session, monkeypatch):
    # Mockear el resultado de get_tablero
    monkeypatch.setattr('src.repositories.board_repository.get_tablero', mock_get_tablero)

    # Crear un mock de la consulta de la ficha
    ficha_mock = Mock(color=Color.ROJO)
    mock_db_session.query().filter().first.return_value = ficha_mock

    # Llamar a la función
    color = get_color_of_ficha(1, 1, game_id=1, db=mock_db_session)

    # Verificar que el color es el esperado
    assert color == Color.ROJO

def test_get_color_of_ficha_sin_ficha(mock_db_session, monkeypatch):
    # Mockear el resultado de get_tablero
    monkeypatch.setattr('src.repositories.board_repository.get_tablero', mock_get_tablero)

    # Simular que no se encuentra ninguna ficha
    mock_db_session.query().filter().first.return_value = None

    # Llamar a la función
    color = get_color_of_ficha(1, 1, game_id=1, db=mock_db_session)

    # Verificar que el color es None
    assert color is None

if __name__ == "__main__":
    pytest.main()
