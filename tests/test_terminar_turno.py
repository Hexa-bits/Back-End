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
from src.main import app
from src.repositories.board_repository import mezclar_fichas
from src.repositories.game_repository import terminar_turno
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

def test_terminar_turno_succesful(test_db, client):
    
    partida = Partida(game_name="partida", max_players=4, jugador_en_turno=0, partida_iniciada=True)
    test_db.add(partida)
    test_db.commit()
        
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

    #turno_actual = partida.jugador_en_turno
    #id_next_player = (turno_actual + 1) % 4
    #next_player = test_db.query(Jugador).filter(Jugador.partida_id == partida.id, Jugador.turno == id_next_player).first()

    #Testeo el endpoint usando la base de datos que cree
    with patch("src.db.get_db"), \
         patch("src.routers.game.get_current_turn_player"), \
         patch("src.routers.game.game_manager.is_tablero_parcial", return_value=False), \
         patch("src.routers.game.terminar_turno") as mock_terminar_turno, \
         patch("src.routers.game.repartir_cartas", return_value= None):
        
        mock_terminar_turno.return_value = terminar_turno(partida.id, test_db)

        response = client.put("/game/end-turn", json={"game_id": partida.id})

        assert response.status_code == 200
        #assert response.json() == {"id_player": next_player.id, "name_player": next_player.nombre}
        assert response.json() == {"id_player": 2 , "name_player": "Jugador2"}

def test_terminar_turno_unsuccesful(test_db, client):

    with patch("src.db.get_db"):
        with patch("src.routers.game.terminar_turno") as mock_terminar_turno:
            mock_terminar_turno.side_effect = IntegrityError("Error de DB", params=None, orig=None)

            response = client.put("/game/end-turn", json={"game_id": 1})

            assert response.status_code == 500
            assert response.json() == {"detail": "Error al finalizar el turno"}
