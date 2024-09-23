import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.models.partida import Partida
from src.models.inputs_front import Partida_config


@pytest.fixture(scope='function')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        yield db


def cheq_entity(entity: object, dicc: dict) -> bool:
    res = True
    for (key, des) in dicc.items():
        atributo = getattr(entity, key, None)
        res = atributo == des
        if (not res):
            break
    return res 

def mock_add_partida(config: Partida_config) -> int:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        partida = Partida(game_name=config.game_name, max_players=config.max_players)
        test_db.add(partida)
        test_db.commit()
        test_db.refresh(partida)
        return partida.id