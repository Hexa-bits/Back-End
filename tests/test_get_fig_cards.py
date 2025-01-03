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

@patch("src.routers.game.get_cartasFigura_player")
@patch("src.routers.game.list_fig_cards")
def test_get_fig_cards_endpoint_3cards(mock_list_movs, mock_get_cards):
    cards_fig = [
        PictureCard(figura=Picture.figura1, estado=CardState.mano),
        PictureCard(figura=Picture.figura2, estado=CardState.mano),
        PictureCard(figura=Picture.figura3, estado=CardState.mano)
    ]

    mock_list_movs.side_effect = lambda player_id, db: mock_list_fig_cards(cards_fig)
    mock_get_cards.return_value = cards_fig

    response = client.get("/game/my-fig-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp ["fig_cant"] == 3
    assert json_resp ["fig_cards"] == [
                                        {"id": cards_fig[0].id, "fig": Picture.figura1.value, "blocked": False},
                                        {"id": cards_fig[1].id, "fig":Picture.figura2.value, "blocked": False},
                                        {"id": cards_fig[2].id, "fig":Picture.figura3.value, "blocked": False}
                                        ]


@patch("src.routers.game.get_cartasFigura_player")
@patch("src.routers.game.list_fig_cards")
def test_get_fig_cards_endpoint_3cards_bloq(mock_list_movs, mock_get_cards):
    cards_fig = [
        PictureCard(figura=Picture.figura1, estado=CardState.mano),
        PictureCard(figura=Picture.figura2, estado=CardState.mano),
        PictureCard(figura=Picture.figura3, estado=CardState.bloqueada)
    ]

    mock_list_movs.side_effect = lambda player_id, db: mock_list_fig_cards(cards_fig)
    mock_get_cards.return_value = cards_fig

    response = client.get("/game/my-fig-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp ["fig_cant"] == 3
    assert json_resp ["fig_cards"] == [
                                        {"id": cards_fig[0].id, "fig": Picture.figura1.value, "blocked": False},
                                        {"id": cards_fig[1].id, "fig":Picture.figura2.value, "blocked": False}
                                        ]


@patch("src.routers.game.get_cartasFigura_player")
@patch("src.routers.game.list_fig_cards")
def test_get_fig_cards_endpoint_2cards(mock_list_movs, mock_get_cards):
    cards_fig = [
        PictureCard(figura=Picture.figura1, estado=CardState.mano),
        PictureCard(figura=Picture.figura2, estado=CardState.mano)
    ]

    mock_list_movs.side_effect = lambda player_id, db: mock_list_fig_cards(cards_fig)
    mock_get_cards.return_value = cards_fig

    response = client.get("/game/my-fig-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp ["fig_cant"] == 2
    assert json_resp ["fig_cards"] == [
                                        {"id": cards_fig[0].id, "fig": Picture.figura1.value, "blocked": False},
                                        {"id": cards_fig[1].id, "fig":Picture.figura2.value, "blocked": False}
                                        ]


@patch("src.routers.game.get_cartasFigura_player")
@patch("src.routers.game.list_fig_cards")
def test_get_fig_cards_endpoint_1card(mock_list_movs, mock_get_cards):
    cards_fig = [PictureCard(figura=Picture.figura1, estado=CardState.mano)]

    mock_list_movs.side_effect = lambda player_id, db: mock_list_fig_cards(cards_fig)
    mock_get_cards.return_value = cards_fig

    response = client.get("/game/my-fig-card?player_id=1")

    mock_list_movs.assert_called_once_with(1, ANY)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp ["fig_cant"] == 1
    assert json_resp ["fig_cards"] == [{"id": cards_fig[0].id, "fig": Picture.figura1.value, "blocked": False}]
    

def test_get_fig_enpoint_exception_list():
    with patch("src.routers.game.list_fig_cards", side_effect=IntegrityError("Error de integridad", 
                                                            params=None, 
                                                            orig=None)) as mock_list_card:
        response = client.get("/game/my-fig-card?player_id=1")
        
        mock_list_card.assert_called_once_with(1, ANY)
        assert response.status_code == 500
        json_resp = response.json()
        assert json_resp["detail"] == "Fallo en la base de datos"
