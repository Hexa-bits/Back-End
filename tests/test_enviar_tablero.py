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
from src.models.color_enum import Color
from src.main import app
from src.routers.game import game_manager
from src.repositories.board_repository import get_box_cards, get_tablero
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.fixture
def client():
    return TestClient(app)

def test_enviar_tablero_succesful_real(test_db, client):
    
    partida = Partida(game_name="partida", max_players=4, jugador_en_turno=0, partida_iniciada=True)
    test_db.add(partida)
    test_db.commit()
    
    game_manager.create_game(partida.id)

    #Agrego un tablero a la partida
    tablero = Tablero(partida_id=partida.id, color_prohibido=None)
    test_db.add(tablero)
    test_db.commit()
    test_db.refresh(tablero)

    #Agrego 36 fichas al tablero 6x6, cada una con una posicion x,y y un color
    for i in range(1,7):
        for j in range(1,7):
            box_card = FichaCajon(tablero_id=tablero.id, x_pos=i, y_pos=j, color=Color.ROJO)
            test_db.add(box_card)
            test_db.commit()
            test_db.refresh(box_card)


    with patch("src.db.get_db"):
        with patch("src.routers.game.get_box_cards") as mock_get_box_cards:
            with patch("src.routers.game.get_tablero", return_value = get_tablero(partida.id, test_db)):
                mock_get_box_cards.return_value = get_box_cards(partida.id, test_db)

                response = client.get("/game/board?game_id=" + str(partida.id))

                assert response.status_code == 200

                list_expected = []
                for i in range(1, 7):
                    for j in range(1, 7):
                        list_expected.append({"x": i, "y": j, "color": 1})
                
                #Se espera un parcial: False ya que por defecto el tablero es real
                response_expected = {"fichas": list_expected, "forbidden_color": 0, "parcial": False}
                assert response.json() == response_expected


def test_enviar_tablero_unsuccesful(client):

    with patch("src.db.get_db"):
        with patch("src.routers.game.get_box_cards") as mock_terminar_turno:
            mock_terminar_turno.side_effect = IntegrityError("Error de DB", params=None, orig=None)

            response = client.get("/game/board?game_id=1")

            assert response.status_code == 500
            assert response.json() == {"detail": "Error al obtener el tablero"}
