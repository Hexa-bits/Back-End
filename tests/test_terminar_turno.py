import pytest
from asyncio import sleep
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
from src.main import app, get_db 
from src.repositories.board_repository import mezclar_fichas
from src.repositories.game_repository import terminar_turno
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_terminar_turno_succesful(test_db, client):
    
    # Define qué retornará get_db
    async def mock_get_db():
        yield test_db
    app.dependency_overrides[get_db] = mock_get_db

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

    #Testeo el endpoint usando la base de datos que cree
    #with patch("src.main.get_db"), \
    with patch("src.main.get_current_turn_player"), \
         patch("src.main.game_manager.is_tablero_parcial", return_value=False), \
         patch("src.main.terminar_turno") as mock_terminar_turno, \
         patch("src.main.repartir_cartas", return_value= None), \
         patch("src.main.game_manager.set_jugador_en_turno_id"), \
         patch("src.main.timer_handler", side_effect= await sleep(2)) as mock_timer:
        
        mock_terminar_turno.return_value = terminar_turno(partida.id, test_db)

        response = client.put("/game/end-turn", json={"game_id": partida.id})
        assert response.status_code == 200
        assert response.json() == {"id_player": 2 , "name_player": "Jugador2"}
        mock_timer.assert_awaited_once_with(partida.id, test_db)

def test_terminar_turno_unsuccesful(test_db, client):

    with patch("src.main.get_db"):
        with patch("src.main.terminar_turno") as mock_terminar_turno:
            mock_terminar_turno.side_effect = IntegrityError("Error de DB", params=None, orig=None)

            response = client.put("/game/end-turn", json={"game_id": 1})

            assert response.status_code == 500
            assert response.json() == {"detail": "Error al finalizar el turno"}
