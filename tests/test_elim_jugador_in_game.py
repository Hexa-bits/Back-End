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
from src.models.utils import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from unittest.mock import ANY
import json

from sqlalchemy.exc import IntegrityError


client = TestClient(app)

@patch("src.main.delete_player")
def test_endpoint_leave_in_game_anf (mock_delete_jugador):
    mock_delete_jugador.side_effect = lambda jugador, db: mock_delete_player(4, empezada=True)
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", return_value = Jugador(nombre="player_1", id=1, es_anfitrion=True, partida_id=1)) as mock_get_jugador:
        with patch("src.main.get_Partida", return_value = Partida(game_name="partida", max_players=4, id=1, partida_iniciada=True)) as mock_get_partida:
            response = client.put(url="/game/leave", json=info_leave)

            leave_lobby = Leave_config(**info_leave)
            mock_delete_jugador.assert_called_once_with(mock_get_jugador.return_value, ANY)
            mock_get_jugador.assert_called_once_with(leave_lobby.id_user, ANY)
            mock_get_partida.assert_called_once_with(leave_lobby.game_id, ANY)
            assert response.status_code == 204


@patch("src.main.delete_player")
def test_endpoint_leave_in_game (mock_delete_jugador):
    mock_delete_jugador.side_effect = lambda jugador, db: mock_delete_player(4, empezada=True)
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", return_value = Jugador(nombre="player_1", id=1, es_anfitrion=False, partida_id=1)) as mock_get_jugador:
        with patch("src.main.get_Partida", return_value = Partida(game_name="partida", max_players=4, id=1, partida_iniciada=True)) as mock_get_partida:
            response = client.put(url="/game/leave", json=info_leave)

            leave_lobby = Leave_config(**info_leave)
            mock_delete_jugador.assert_called_once_with(mock_get_jugador.return_value, ANY)
            mock_get_jugador.assert_called_once_with(leave_lobby.id_user, ANY)
            mock_get_partida.assert_called_once_with(leave_lobby.game_id, ANY)
            assert response.status_code == 204


@patch("src.main.delete_player")
def test_endpoint_leave_in_game_elim_partida (mock_delete_jugador):
    mock_delete_jugador.side_effect = lambda jugador, db: mock_delete_player(1, empezada=True)
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", return_value = Jugador(nombre="player_1", id=1, es_anfitrion=False, partida_id=1)) as mock_get_jugador:
        with patch("src.main.get_Partida", return_value = Partida(game_name="partida", max_players=2, id=1, partida_iniciada=True)) as mock_get_partida:
            response = client.put(url="/game/leave", json=info_leave)

            leave_lobby = Leave_config(**info_leave)
            mock_delete_jugador.assert_called_once_with(mock_get_jugador.return_value, ANY)
            mock_get_jugador.assert_called_once_with(leave_lobby.id_user, ANY)
            mock_get_partida.assert_called_once_with(leave_lobby.game_id, ANY)
            assert response.status_code == 204

