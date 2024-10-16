import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from src.repositories.board_repository import *
from src.models.fichas_cajon import FichaCajon, Color  # Ajustar importación según tu estructura
from src.models.tablero import Tablero
from src.models.partida import Partida
from src.models.utils import Coords
from .test_helpers import test_db
import numpy as np

@pytest.fixture
def board_test(test_db: Session) -> Session:
    """Inyección de base de datos de prueba para cada test."""
    
    # Poblar la base de datos
    partida = Partida(id=1, game_name="partida", max_players=4, partida_iniciada=True)
    tablero = Tablero(id=1, partida_id=1)
    
    ficha1 = FichaCajon(id=1, x_pos=1, y_pos=1, color=Color.ROJO, tablero_id=1)
    ficha2 = FichaCajon(id=2, x_pos=2, y_pos=2, color=Color.VERDE, tablero_id=1)

    test_db.add_all([partida, tablero, ficha1, ficha2])
    test_db.commit()
    return test_db

@pytest.fixture
def initial_fichas() -> tuple[FichaCajon, FichaCajon]:
    """Fixture con las fichas iniciales para comparaciones."""
    return (
        FichaCajon(id=1, x_pos=1, y_pos=1, color=Color.ROJO, tablero_id=1),
        FichaCajon(id=2, x_pos=2, y_pos=2, color=Color.VERDE, tablero_id=1),
    )

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

def test_switch_cartasCajon_OK (board_test: Session,
                                initial_fichas: tuple[FichaCajon, FichaCajon]):
    """
    Testeo que la función swap_fichasCajon funcione correctamente con los 
    parametros adecuados.
    """
    partida = MagicMock(id=1)
    tupla_coords = (Coords(x=1, y=1), Coords(x=2, y=2))

    result = swap_fichasCajon(partida.id, tupla_coords, board_test)
    assert result is None, f'No devuelve None, sino {result}'

    #Obtengo las fichasCajon que la db de prueba 
    ficha1 = get_fichaCajon_coords(partida.id, tupla_coords[0], board_test)
    ficha2 = get_fichaCajon_coords(partida.id, tupla_coords[1], board_test)

    #Verfico que las fichas se hayan swappeado, comparandolas con sus instancias previas
    assert ficha1 is not None, "La 'ficha1' es None"
    assert ficha2 is not None, "La 'ficha2' es None"
    assert isinstance(ficha1, FichaCajon), f'El tipo no debería ser {type(ficha1)}'
    assert isinstance(ficha2, FichaCajon), f'El tipo no debería ser {type(ficha2)}'
    assert ficha1 == initial_fichas[0], "No se intercambian fichas"
    assert ficha2 == initial_fichas[1], "No se intercambian fichas"

def test_switch_cartasCajon_not_in_db(board_test: Session):
    """
    Testeo que la función swap_fichasCajon falle si es que el trata de obtener la info
    de una partida que no existe 
    """
    partida = MagicMock(id=2)
    tupla_coords = (Coords(x=1, y=1), Coords(x=2, y=2))
    
    with pytest.raises(ValueError, match="Una o ambas fichasCajon no existe en la db"):
        swap_fichasCajon(partida.id, tupla_coords, board_test)

def test_switch_cartasCajon_null_param(board_test: Session):
    """
    Testeo que la función swap_fichasCajon falle si es que se pasan parametros None 
    """
    with pytest.raises(TypeError):
        swap_fichasCajon(None, None, board_test)

        
if __name__ == "__main__":
    pytest.main()
