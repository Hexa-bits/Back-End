import pytest
from sqlalchemy import create_engine
from src.db import Base
from sqlalchemy.orm import sessionmaker
from src.models.partida import Partida
from src.models.inputs_front import *
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from unittest.mock import Mock
from sqlalchemy.orm import Session
from src.repositories.board_repository import get_valid_detected_figures, get_color_of_ficha, movimiento_parcial
from src.models.fichas_cajon import FichaCajon, Color  # Ajustar importación según tu estructura
import numpy as np



@pytest.fixture(scope='module')
def test_db():
    # Crea un motor de base de datos en memoria para pruebas
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    # Crea una sesión
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()

def test_movimiento_parcial(test_db):
    partida = Partida(id=1, game_name = 'test_board')
    game_id = partida.id
    moveCard = MovementCard(id=1, estado=CardStateMov.mano)

    tablero = Tablero(id=1, partida_id = 1)
    fichacajon0 = FichaCajon(x_pos=1, y_pos=1, color=Color.ROJO, tablero_id=1)
    fichacajon1 = FichaCajon(x_pos=2, y_pos=2, color=Color.AZUL, tablero_id=1)

    test_db.add(tablero)
    test_db.add(fichacajon0)
    test_db.add(fichacajon1)
    test_db.commit()

    ficha0 = Ficha(x_pos = 1, y_pos = 1)
    ficha1 = Ficha(x_pos = 2, y_pos = 2)
    coord = (ficha0, ficha1)

    movimiento_parcial(game_id, moveCard, coord, test_db)

    ficha0_actualizada = test_db.query(FichaCajon).filter_by(x_pos=1, y_pos=1).first()
    ficha1_actualizada = test_db.query(FichaCajon).filter_by(x_pos=2, y_pos=2).first()

    assert ficha0_actualizada.color == Color.AZUL
    assert ficha1_actualizada.color == Color.ROJO
    assert moveCard.estado == CardStateMov.descartada
    

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
