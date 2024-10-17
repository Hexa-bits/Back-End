import pytest
from sqlalchemy.exc import IntegrityError
from src.db import Base
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador

from src.models.utils import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon

def test_create_partida(test_db):
    configuracion = {"game_name": "primera",
                    "max_players": 4,
                    "partida_iniciada": True
                    }
    partida = Partida(**configuracion)
    test_db.add(partida)
    test_db.commit()
    test_db.refresh(partida)

    assert cheq_entity(partida, configuracion)
    assert partida.jugador_en_turno == 0
    assert partida.id == 1

def test_multi_partida(test_db):
    for i in range(20):
        configuracion = {"game_name": str(i),
                        "max_players": 4}
        partida = Partida(**configuracion)
        test_db.add(partida)
        test_db.commit()
        test_db.refresh(partida)

        assert cheq_entity(partida, configuracion)
        assert partida.jugador_en_turno == 0
        assert partida.id == i+1

def test_create_partida_invalid_nulls(test_db):    
    partida = Partida()
    
    with pytest.raises(IntegrityError):
        test_db.add(partida)
        test_db.commit()
