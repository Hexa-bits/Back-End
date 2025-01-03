import pytest
from sqlalchemy.exc import IntegrityError
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador
from src.models.utils import Partida_config
from src.models.partida import Partida

from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon

def test_create_jugador(test_db):
    configuracion_partida = {"game_name": "primera",
                    "max_players": 4, 
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
        configuracion_partida = {"game_name": str(i),
                                "max_players": 4}
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