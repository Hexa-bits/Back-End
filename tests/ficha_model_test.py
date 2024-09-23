import enum
import pytest
from sqlalchemy import inspect, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from src.models.jugadores import Jugador
from src.models.inputs_front import Partida_config
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

def cheq_ficha_cajon(ficha_cajon: FichaCajon, dicc: dict) -> bool:
    res = True
    for (key, des) in dicc.items():
        atributo = getattr(ficha_cajon, key, None)
        if isinstance(atributo, enum.Enum):
            res = atributo.name == des  # Compara el nombre del Enum con la cadena
        else:
            res = atributo == des
        if (not res):
            break
    return res

def test_create_ficha_cajon(test_db):
    configuracion = {"x_pos": 1, "y_pos": 2, "color": "AZUL"}
    ficha_cajon = FichaCajon(**configuracion)
    test_db.add(ficha_cajon)
    test_db.commit()
    test_db.refresh(ficha_cajon)

    assert cheq_ficha_cajon(ficha_cajon, configuracion)
    assert ficha_cajon.id == 1
    assert ficha_cajon.x_pos == 1
    assert ficha_cajon.y_pos == 2
    assert ficha_cajon.color == Color.AZUL

def test_multi_ficha_cajon(test_db):
    for i in range(20):
        configuracion = {"x_pos": 1, "y_pos": 2, "color": "AZUL"}
        ficha_cajon = FichaCajon(**configuracion)
        test_db.add(ficha_cajon)
        test_db.commit()
        test_db.refresh(ficha_cajon)

        assert cheq_ficha_cajon(ficha_cajon, configuracion)
        assert ficha_cajon.id == i+1
        assert ficha_cajon.x_pos == 1
        assert ficha_cajon.y_pos == 2
        assert ficha_cajon.color == Color.AZUL
