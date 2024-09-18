import pytest
from sqlalchemy.exc import IntegrityError
from src.db import Base
from .test_helpers import test_db, cheq_entity
from src.models.partida import Partida

def test_create_partida(test_db):
    configuracion = {"nombre": "primera",
                    "cantidad_max_jugadores": 4,
                    "cantidad_min_jugadores": 2, 
                    "partida_iniciada": True}
    partida = Partida(**configuracion)
    test_db.add(partida)
    test_db.commit()
    test_db.refresh(partida)

    assert cheq_entity(partida, configuracion)
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

        assert cheq_entity(partida, configuracion)
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
