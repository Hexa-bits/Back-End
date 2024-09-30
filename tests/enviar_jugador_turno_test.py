
import pytest
from sqlalchemy.exc import IntegrityError
from src.consultas import jugador_en_turno
from src.db import Base
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador
from src.models.inputs_front import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.main import app 
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

def test_enviar_jugador_turno_succesful(test_db, client):

    partida = Partida(game_name="partida", max_players=4, jugador_en_turno=0, partida_iniciada=True)
    test_db.add(partida)
    test_db.commit()

    #Agrego 4 jugadores a la partida
    jugador1 = Jugador(nombre="jugador1", partida_id=partida.id, es_anfitrion=True, turno=0)
    jugador2 = Jugador(nombre="jugador2", partida_id=partida.id, es_anfitrion=False, turno=1)
    jugador3 = Jugador(nombre="jugador3", partida_id=partida.id, es_anfitrion=False, turno=2)
    jugador4 = Jugador(nombre="jugador4", partida_id=partida.id, es_anfitrion=False, turno=3)

    test_db.add(jugador1)
    test_db.add(jugador2)
    test_db.add(jugador3)
    test_db.add(jugador4)
    test_db.commit()

    with patch("src.main.get_db"):
        with patch("src.main.jugador_en_turno") as mock_jugador_en_turno:
            mock_jugador_en_turno.return_value = jugador_en_turno(partida.id, test_db)

            response = client.get("/game/current-turn?game_id=" + str(partida.id))

            assert response.status_code == 200

            response_expected = {"id_player": 1, "name_player": "jugador1"}
            assert response.json() == response_expected




def test_enviar_jugador_turno_unsuccesful(client):

    with patch("src.main.get_db"):
        with patch("src.main.jugador_en_turno") as mock_jugador_en_turno:
            mock_jugador_en_turno.side_effect = IntegrityError("Error de DB", params=None, orig=None)

            response = client.get("/game/current-turn?game_id=1")

            assert response.status_code == 500
            assert response.json() == {"detail": "Error al obtener el jugador actual en turno"}