import pytest
from fastapi.testclient import TestClient
from src.main import app
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.models.partida import Partida
from src.models.inputs_front import *
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov

client = TestClient(app)

def test_use_mov_card():
 
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)):
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio)):
                with patch('src.main.is_valid_move', return_value = True):
                    with patch('src.main.movimiento_parcial', return_value = None):
                        response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                            "id_mov_card": 1,
                                                                            "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                    {"x_pos": 4, "y_pos": 4}]
                                                                            })
                            
                        assert response.status_code == 200
        game_manager_mock.apilar_carta_y_ficha.assert_called_once_with(1, 1, (Ficha(x_pos=2, y_pos=2), Ficha(x_pos=4, y_pos=4)))


def test_use_mov_card_invalid():
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)):
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio)):
                with patch('src.main.is_valid_move', return_value = False):
                    with patch('src.main.movimiento_parcial', return_value = None):
                        response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                            "id_mov_card": 1,
                                                                            "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                    {"x_pos": 2, "y_pos": 3}]
                                                                            })
                            
                        assert response.status_code == 400
                        assert response.json() == {'detail': "Movimiento invalido"}
        game_manager_mock.apilar_carta_y_ficha.assert_not_called()
    

def test_use_mov_card_error():
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)):
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio)):
                with patch('src.main.is_valid_move', return_value = True):
                    with patch('src.main.movimiento_parcial', side_effect = SQLAlchemyError):
                        response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                            "id_mov_card": 1,
                                                                            "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                    {"x_pos": 4, "y_pos": 4}]
                                                                            })
                            
                        assert response.status_code == 500
                        assert response.json() == {'detail': "Fallo en la base de datos"}
        game_manager_mock.apilar_carta_y_ficha.assert_not_called()