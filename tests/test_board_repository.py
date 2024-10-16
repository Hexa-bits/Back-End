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
from src.repositories.board_repository import movimiento_parcial


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
    