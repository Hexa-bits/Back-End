import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base

@pytest.fixture(scope='function')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        yield db

def cheq_entity(partida: object, dicc: dict) -> bool:
    res = True
    for (key, des) in dicc.items():
        atributo = getattr(partida, key, None)
        res = atributo == des
        if (not res):
            break
    return res 