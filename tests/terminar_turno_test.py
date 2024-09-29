import pytest
from sqlalchemy.exc import IntegrityError
from src.db import Base
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador
from src.models.inputs_front import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.main import app 
from src.consultas import mezclar_fichas
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

def test_terminar_turno_succesful(test_db, client):
    
    partida = Partida(game_name="partida", max_players=4, jugador_en_turno=0, partida_iniciada=True)
    test_db.add(partida)
    test_db.commit()
    
    print(partida.id)
    
    #Agrego 4 jugadores a la partida
    jugador1 = Jugador(nombre="Jugador1", es_anfitrion=True, partida_id=partida.id, turno=0)
    jugador2 = Jugador(nombre="Jugador2", es_anfitrion=False, partida_id=partida.id, turno=1)
    jugador3 = Jugador(nombre="Jugador3", es_anfitrion=False, partida_id=partida.id, turno=2)
    jugador4 = Jugador(nombre="Jugador4", es_anfitrion=False, partida_id=partida.id, turno=3)

    test_db.add(jugador1)
    test_db.add(jugador2)
    test_db.add(jugador3)
    test_db.add(jugador4)
    test_db.commit()

    with patch('src.main.get_db'):
        response = client.put("/game/end-turn", json={"game_id": partida.id})

        assert response.status_code == 200
        assert response.json() == {"detail": "Turno finalizado"}