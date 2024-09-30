from src.main import app
import pytest

from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .test_helpers import mock_add_partida, cheq_entity
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.inputs_front import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from unittest.mock import ANY


client = TestClient(app)

@patch("src.routers.home.add_partida")
def test_endpoint_partida (mock_add_game):
    mock_add_game.side_effect = lambda partida, db: mock_add_partida(partida)
    config = {"id_user": 1, "game_name": "partida", "max_players": 4}
    
    response = client.post("/home/create-config", json=config)
        
    config_partida = Partida_config(**config)
    mock_add_game.assert_called_once_with(config_partida, ANY)
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp ["id"] == 1


def test_endpoint_partida_exception_add_partida ():
    config = {"id_user": 1, "game_name": "partida", "max_players": 4}
    with patch("src.routers.home.add_partida", side_effect=IntegrityError("Error de integridad", 
                                                                    params=None, 
                                                                    orig=None)) as mock_add_player:
        response = client.post("/home/create-config", json=config)
        
        config_partida = Partida_config(**config)
        mock_add_player.assert_called_once_with(config_partida, ANY)
        assert response.status_code == 500
        json_resp = response.json()
        assert json_resp["detail"] == "Fallo en la base de datos"


def test_endpoint_partida_invalid_max ():
    config = {"id_user": 1, "game_name": "partida", "max_players": 1}
    with patch("src.routers.home.add_partida", return_value=1) as mock_add_player:
        response = client.post("/home/create-config", json=config)
        
        mock_add_player.assert_not_called()
        assert response.status_code == 422
        json_resp = response.json()
        assert json_resp ["detail"] == [{'type': 'greater_than',
                                        'loc': ['body', 'max_players'],
                                        'msg': 'Input should be greater than 1',
                                        'input': 1, 'ctx': {'gt': 1}}]


def test_endpoint_partida_invalid_name_length ():
    config = {"id_user": 1, "game_name": "abcdefghijklmnopq", "max_players": 4}
    with patch("src.routers.home.add_partida", return_value=1) as mock_add_player:
        response = client.post("/home/create-config", json=config)
        
        mock_add_player.assert_not_called()
        assert response.status_code == 422
        json_resp = response.json()
        assert json_resp ["detail"] == [{'type': 'string_too_long', 
                                            'loc': ['body', 'game_name'], 
                                            'msg': 'String should have at most 10 characters', 
                                            'input': 'abcdefghijklmnopq', 'ctx': {'max_length': 10}}]
    

def test_endpoint_partida_invalid_name_str ():
    config = {"id_user": 1, "game_name": None, "max_players": 4}
    with patch("src.routers.home.add_partida", return_value=1) as mock_add_player:
        response = client.post("/home/create-config", json=config)
        
        mock_add_player.assert_not_called()
        assert response.status_code == 422
        json_resp = response.json()
        assert json_resp ["detail"] == [{'input': None,
                                        'loc': ['body', 'game_name'],
                                        'msg': 'Input should be a valid string',
                                        'type': 'string_type'}]
            

def test_endpoint_partida_invalid_name ():
    config = {"id_user": "str", "game_name": "partida", "max_players": 4, "extra": 1}
    with patch("src.routers.home.add_partida", return_value=1) as mock_add_player:
        response = client.post("/home/create-config", json=config)
            
        mock_add_player.assert_not_called()
        assert response.status_code == 422
        json_resp = response.json()
        assert json_resp ["detail"] == [{'type': 'int_parsing',
                                        'loc': ['body', 'id_user'],
                                        'msg': 'Input should be a valid integer, unable to parse string as an integer', 
                                        'input': 'str'}]