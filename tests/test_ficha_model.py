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

def cheq_box_card(box_card: FichaCajon, dicc: dict) -> bool:
    res = True
    for (key, des) in dicc.items():
        atributo = getattr(box_card, key, None)
        if isinstance(atributo, enum.Enum):
            res = atributo.name == des  # Compara el nombre del Enum con la cadena
        else:
            res = atributo == des
        if (not res):
            break
    return res

def test_create_box_card(test_db):
    configuracion = {"x_pos": 1, "y_pos": 2, "color": "AZUL"}
    box_card = FichaCajon(**configuracion)
    test_db.add(box_card)
    test_db.commit()
    test_db.refresh(box_card)

    assert cheq_box_card(box_card, configuracion)
    assert box_card.id == 1
    assert box_card.x_pos == 1
    assert box_card.y_pos == 2
    assert box_card.color == Color.AZUL

def test_multi_box_card(test_db):
    for i in range(20):
        configuracion = {"x_pos": 1, "y_pos": 2, "color": "AZUL"}
        box_card = FichaCajon(**configuracion)
        test_db.add(box_card)
        test_db.commit()
        test_db.refresh(box_card)

        assert cheq_box_card(box_card, configuracion)
        assert box_card.id == i+1
        assert box_card.x_pos == 1
        assert box_card.y_pos == 2
        assert box_card.color == Color.AZUL
