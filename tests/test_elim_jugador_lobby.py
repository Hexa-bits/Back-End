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

@patch("src.main.delete_players_lobby")
def test_endpoint_leave_lobby_anf (mock_delete_jugadores):
    mock_delete_jugadores.side_effect = lambda partida, db: mock_delete_players_lobby(partida.max_players, partida.partida_iniciada)
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", return_value = Jugador(nombre="player_1", id=1, es_anfitrion=True, partida_id=1)) as mock_get_jugador:
        with patch("src.main.get_Partida", return_value = Partida(game_name="partida", max_players=4, id=1)) as mock_get_partida:
            response = client.put(url="/game/leave", json=info_leave)

            leave_lobby = Leave_config(**info_leave)
            mock_delete_jugadores.assert_called_once_with(mock_get_partida.return_value, ANY)
            mock_get_jugador.assert_called_once_with(leave_lobby.id_user, ANY)
            mock_get_partida.assert_called_once_with(leave_lobby.game_id, ANY)
            assert response.status_code == 204


@patch("src.main.delete_player")
def test_endpoint_leave_lobby (mock_delete_jugador):
    mock_delete_jugador.side_effect = lambda jugador, db: mock_delete_player(4, empezada=False)
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", return_value = Jugador(nombre="player_1", id=1, es_anfitrion=False, partida_id=1)) as mock_get_jugador:
        with patch("src.main.get_Partida", return_value = Partida(game_name="partida", max_players=4, id=1)) as mock_get_partida:
            response = client.put(url="/game/leave", json=info_leave)

            leave_lobby = Leave_config(**info_leave)
            mock_delete_jugador.assert_called_once_with(mock_get_jugador.return_value, ANY)
            mock_get_jugador.assert_called_once_with(leave_lobby.id_user, ANY)
            mock_get_partida.assert_called_once_with(leave_lobby.game_id, ANY)
            assert response.status_code == 204


@patch("src.main.delete_player")
def test_endpoint_leave_lobby_elim_partida (mock_delete_jugador):
    mock_delete_jugador.side_effect = lambda jugador, db: mock_delete_player(2, empezada=False)
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", return_value = Jugador(nombre="player_1", id=1, es_anfitrion=False, partida_id=1)) as mock_get_jugador:
        with patch("src.main.get_Partida", return_value = Partida(game_name="partida", max_players=2, id=1)) as mock_get_partida:
            response = client.put(url="/game/leave", json=info_leave)

            leave_lobby = Leave_config(**info_leave)
            mock_delete_jugador.assert_called_once_with(mock_get_jugador.return_value, ANY)
            mock_get_jugador.assert_called_once_with(leave_lobby.id_user, ANY)
            mock_get_partida.assert_called_once_with(leave_lobby.game_id, ANY)
            assert response.status_code == 204


def test_endpoint_leave_lobby_invalid_game_type ():
    info_leave = {"id_user": 1, "game_id": "str"}
    with patch("src.main.get_Jugador") as mock_get_jugador:
        response = client.put(url="/game/leave", json=info_leave)

        mock_get_jugador.assert_not_called()
        assert response.status_code == 422
        json_resp = response.json()
        assert json_resp["detail"] == [{'type': 'int_parsing', 'loc': ['body', 'game_id'], 
                                        'msg': 'Input should be a valid integer, unable to parse string as an integer',
                                        'input': 'str'}]


def test_endpoint_leave_lobby_invalid_player_type ():
    info_leave = {"id_user": "str", "game_id": 1}
    with patch("src.main.get_Jugador") as mock_get_jugador:
        response = client.put(url="/game/leave", json=info_leave)

        mock_get_jugador.assert_not_called()
        assert response.status_code == 422
        json_resp = response.json()
        assert json_resp["detail"] == [{'type': 'int_parsing', 'loc': ['body', 'id_user'],
                                      'msg': 'Input should be a valid integer, unable to parse string as an integer', 
                                      'input': 'str'}]
        

def test_endpoint_leave_lobby_invalid_player_num ():
    info_leave = {"id_user": -1, "game_id": 1}
    with patch("src.main.get_Jugador") as mock_get_jugador:
        response = client.put(url="/game/leave", json=info_leave)

        mock_get_jugador.assert_not_called()
        assert response.status_code == 422
        json_resp = response.json()
        assert json_resp["detail"] == [{'type': 'greater_than', 'loc': ['body', 'id_user'],
                                        'msg': 'Input should be greater than 0',
                                        'input': -1, 'ctx': {'gt': 0}}]


def test_endpoint_leave_lobby_exception_add_partida ():
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", side_effect=IntegrityError("Error de integridad", 
                                                                    params=None, 
                                                                    orig=None)) as mock_add_player:
        response = client.put(url="/game/leave", json=info_leave)
        
        config = Leave_config(**info_leave)
        mock_add_player.assert_called_once_with(config.id_user, ANY)
        assert response.status_code == 500
        json_resp = response.json()
        assert json_resp["detail"] == "Fallo en la base de datos"


def test_endpoint_leave_lobby_exception_not_found ():
    info_leave = {"id_user": 1, "game_id": 1}
    with patch("src.main.get_Jugador", return_value = None) as mock_add_player:
        response = client.put(url="/game/leave", json=info_leave)
        
        config = Leave_config(**info_leave)
        mock_add_player.assert_called_once_with(config.id_user, ANY)
        assert mock_add_player.return_value is None
        assert response.status_code == 404
        json_resp = response.json()
        assert json_resp["detail"] == f'No existe el jugador: {config.id_user}' 