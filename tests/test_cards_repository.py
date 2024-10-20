import pytest
from src.repositories.cards_repository import *
from src.models.partida import Partida
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.cartamovimiento import MovementCard
from tests.test_helpers import test_db

def test_descartar_carta_figura(test_db):
    jugador1 = Jugador(id=1, nombre="test", partida_id= 1)
    jugador2 = Jugador(id=2, nombre="test", partida_id= 1)
    partida = Partida(id=1, game_name= "test", max_players=2, partida_iniciada=True)

    test_db.add(partida)
    test_db.add(jugador1)
    test_db.add(jugador2)
    test_db.commit()

    carta_figura1 = PictureCard(id=1, estado = CardState.mano, partida_id = 1, jugador_id = 1)
    carta_figura2 = PictureCard(id=2, estado = CardState.mano, partida_id = 1, jugador_id = 1)
    carta_figura3 = PictureCard(id=3, estado = CardState.mano, partida_id = 1, jugador_id = 2)
    carta_figura4 = PictureCard(id=4, estado = CardState.mano, partida_id = 1, jugador_id = 2)

    test_db.add(carta_figura1)
    test_db.add(carta_figura2)
    test_db.add(carta_figura3)
    test_db.add(carta_figura4)
    test_db.commit()

    descartar_carta_figura(1, test_db)

    assert get_cartasFigura_player(jugador1.id, test_db) == [carta_figura2]
    assert get_CartaFigura(1, test_db) == None

    descartar_carta_figura(3, test_db)
    descartar_carta_figura(4, test_db)

    assert get_cartasFigura_player(jugador2.id, test_db) == []
    assert get_CartaFigura(3, test_db) == None
    assert get_CartaFigura(4, test_db) == None