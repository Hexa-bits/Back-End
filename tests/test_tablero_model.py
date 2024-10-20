import enum
import pytest
from sqlalchemy import inspect, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from src.models.jugadores import Jugador

from src.models.utils import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.models.color_enum import Color

@pytest.fixture(scope='function')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()

def cheq_tablero(tablero: Tablero, dicc: dict) -> bool:
    res = True
    for (key, des) in dicc.items():
        atributo = getattr(tablero, key, None)
        if isinstance(atributo, enum.Enum):
            res = atributo.name == des  # Compara el nombre del Enum con la cadena
        else:
            res = atributo == des
        if (not res):
            break
    return res

def test_create_tablero(test_db):
    configuracion = {"color_prohibido": "ROJO"}
    tablero = Tablero(**configuracion)
    test_db.add(tablero)
    test_db.commit()
    test_db.refresh(tablero)

    assert cheq_tablero(tablero, configuracion)
    assert tablero.id == 1
    assert tablero.color_prohibido == Color.ROJO

def test_multi_tablero(test_db):
    for i in range(20):
        configuracion = {"color_prohibido": "AZUL"}
        tablero = Tablero(**configuracion)
        test_db.add(tablero)
        test_db.commit()
        test_db.refresh(tablero)

        assert cheq_tablero(tablero, configuracion)
        assert tablero.id == i+1
        assert tablero.color_prohibido == Color.AZUL
