import pytest
from sqlalchemy.exc import IntegrityError
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador
from src.models.partida import Partida

def test_create_jugador(test_db):
    configuracion_partida = {"nombre": "primera",
                    "cantidad_max_jugadores": 4,
                    "cantidad_min_jugadores": 2, 
                    "partida_iniciada": True}
    partida = Partida(**configuracion_partida)
    test_db.add(partida)
    test_db.commit()
    test_db.refresh(partida)

    configuracion_jugador = {"nombre": "Juan",
                             "es_anfitrion": True,
                             "partida_id": partida.id}

    jugador = Jugador(**configuracion_jugador)
    test_db.add(jugador)
    test_db.commit()
    test_db.refresh(jugador)

    assert cheq_entity(jugador, configuracion_jugador)
    assert jugador.turno == 0
    assert jugador.partida == partida

def test_multi_jugadores(test_db):
    for i in range(20):
        configuracion_partida = {"nombre": str(i),
                                "cantidad_max_jugadores": 4,
                                "cantidad_min_jugadores": 2}
        partida = Partida(**configuracion_partida)
        test_db.add(partida)
        test_db.commit()
        test_db.refresh(partida)

        configuracion_jugador = {"nombre": str(i),
                                "es_anfitrion": False,
                                "partida_id": partida.id}
        
        jugador = Jugador(**configuracion_jugador)
        test_db.add(jugador)
        test_db.commit()
        test_db.refresh(jugador)

        assert cheq_entity(jugador, configuracion_jugador)
        assert jugador.turno == 0
        assert jugador.partida == partida