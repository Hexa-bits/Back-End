from src.main import app
import pytest

from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .test_helpers import *
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.utils import Partida_config
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard, Move 
from src.models.cartafigura import PictureCard
from unittest.mock import ANY

from sqlalchemy.exc import IntegrityError

client = TestClient(app)


@patch("src.routers.game.list_mov_cards")
def test_get_mov_cards_endpoint_3cards(mock_list_movs):
    cards_mov = [
        MovementCard(id=1, movimiento=Move.diagonal_con_espacio, estado=CardStateMov.mano),
        MovementCard(id=2, movimiento=Move.linea_contiguo, estado=CardStateMov.mano),
        MovementCard(id=3, movimiento=Move.linea_con_espacio, estado=CardStateMov.mano)
    ]

    mock_list_movs.side_effect = lambda player_id, db: mock_list_mov_cards(cards_mov)

    response = client.get("/game/my-mov-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp["mov_cards"]) == 3
    assert json_resp ["mov_cards"] == [
                                        {"id": 1, "move": Move.diagonal_con_espacio.value},
                                        {"id": 2, "move": Move.linea_contiguo.value},
                                        {"id": 3, "move": Move.linea_con_espacio.value} 
                                        ]


@patch("src.routers.game.list_mov_cards")
def test_get_mov_cards_endpoint_2cards(mock_list_movs):
    cards_mov = [
        MovementCard(id=1, movimiento=Move.diagonal_con_espacio, estado=CardStateMov.mano),
        MovementCard(id=2, movimiento=Move.linea_contiguo, estado=CardStateMov.mano)
    ]

    mock_list_movs.side_effect = lambda player_id, db: mock_list_mov_cards(cards_mov)

    response = client.get("/game/my-mov-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp ["mov_cards"]) == 2 
    assert json_resp ["mov_cards"] == [
                                        {"id": 1, "move": Move.diagonal_con_espacio.value},
                                        {"id": 2, "move": Move.linea_contiguo.value} 
                                        ]


@patch("src.routers.game.list_mov_cards")
def test_get_mov_cards_endpoint_1card(mock_list_movs):
    cards_mov = [MovementCard(id=1, movimiento=Move.diagonal_con_espacio, estado=CardStateMov.mano)]

    mock_list_movs.side_effect = lambda player_id, db: mock_list_mov_cards(cards_mov)

    response = client.get("/game/my-mov-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp ["mov_cards"]) == 1
    assert json_resp ["mov_cards"] == [
                                        {"id": 1, "move": Move.diagonal_con_espacio.value}, 
                                        ]


def test_get_mov_enpoint_exception_list():
    with patch("src.routers.game.list_mov_cards", side_effect=IntegrityError("Error de integridad", 
                                                            params=None, 
                                                            orig=None)) as mock_list_card:
        response = client.get("/game/my-mov-card?player_id=1")
        
        mock_list_card.assert_called_once_with(1, ANY)
        assert response.status_code == 500
        json_resp = response.json()
        assert json_resp["detail"] == "Fallo en la base de datos"
