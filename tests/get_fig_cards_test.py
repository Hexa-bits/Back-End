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
from src.models.inputs_front import Partida_config
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard, Move 
from src.models.cartafigura import PictureCard
from unittest.mock import ANY

from sqlalchemy.exc import IntegrityError

client = TestClient(app)


@patch("src.main.list_fig_cards")
def test_get_fig_cards_endpoint_fig19(mock_list_movs):
    mock_list_movs.side_effect = lambda player_id, db: mock_list_fig_cards(Picture.figura19)

    response = client.get("/game/my-fig-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    #assert json_resp ["id_fig_card"] == [Move.diagonal_con_espacio.value]


@patch("src.main.list_fig_cards")
def test_get_fig_cards_endpoint_fig1(mock_list_movs):
    mock_list_movs.side_effect = lambda player_id, db: mock_list_fig_cards(Picture.figura1)

    response = client.get("/game/my-fig-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    #assert json_resp ["id_fig_card"] == [Move.linea_contiguo.value]


@patch("src.main.list_fig_cards")
def test_get_fig_cards_endpoint_fig10(mock_list_movs):
    mock_list_movs.side_effect = lambda player_id, db: mock_list_fig_cards(Picture.figura10)

    response = client.get("/game/my-fig-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    #assert json_resp ["id_fig_card"] == [Move.L_derecha.value]


def test_get_fig_enpoint_exception_list():
    with patch("src.main.list_fig_cards", side_effect=IntegrityError("Error de integridad", 
                                                            params=None, 
                                                            orig=None)) as mock_list_card:
        response = client.get("/game/my-fig-card?player_id=1")
        
        mock_list_card.assert_called_once_with(1, ANY)
        assert response.status_code == 500
        json_resp = response.json()
        assert json_resp["detail"] == "Fallo en la base de datos"
