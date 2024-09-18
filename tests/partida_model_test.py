import pytest
from sqlalchemy import inspect, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from src.models.partida import Partida, Base

@pytest.fixture(scope='function')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def cheq_partida(partida: Partida, dicc: dict) -> bool:
    res = True
    for (key, des) in dicc.items():
        atributo = getattr(partida, key, None)
        res = atributo == des
        if (not res):
            break
    return res 

def test_create_user(test_db):
    configuracion = {"nombre": "primera",
                    "cantidad_max_jugadores": 4,
                    "cantidad_min_jugadores": 2, 
                    "partida_iniciada": True}
    partida = Partida(**configuracion)
    test_db.add(partida)
    test_db.commit()
    test_db.refresh(partida)

    assert cheq_partida(partida, configuracion)
    assert partida.cantidad_max_jugadores in range(2, 5)
    assert partida.cantidad_min_jugadores in range(2, 5)
    assert partida.jugador_en_turno == 0
    assert partida.id == 1

def test_multi_partida(test_db):
    for i in range(20):
        configuracion = {"nombre": str(i),
                        "cantidad_max_jugadores": 4,
                        "cantidad_min_jugadores": 2}
        partida = Partida(**configuracion)
        test_db.add(partida)
        test_db.commit()
        test_db.refresh(partida)

        assert cheq_partida(partida, configuracion)
        assert partida.cantidad_max_jugadores in range(2, 5)
        assert partida.cantidad_min_jugadores in range(2, 5)
        assert partida.jugador_en_turno == 0
        assert partida.id == i+1

def test_create_partida_invalid_jugadores(test_db):
    configuracion = {
        "nombre": "segunda", 
        "cantidad_max_jugadores": 5,  
        "cantidad_min_jugadores": 1,  
        "partida_iniciada": True
    }
    
    partida = Partida(**configuracion)
    
    with pytest.raises(IntegrityError):
        test_db.add(partida)
        test_db.commit()

def test_create_partida_invalid_nulls(test_db):
    
    partida = Partida()
    
    with pytest.raises(IntegrityError):
        test_db.add(partida)
        test_db.commit()
