import pytest
from fastapi.testclient import TestClient
from src.main import app, lista_patrones
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
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)) as mock_get_jugador:
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio, 
                                                                                partida_id=1, jugador_id=1)):
                with patch('src.main.get_jugador_en_turno', return_value= mock_get_jugador.return_value):
                    with patch('src.main.is_valid_move', return_value = True):
                        with patch('src.main.movimiento_parcial', return_value = None):
                            response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                                "id_mov_card": 1,
                                                                                "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                        {"x_pos": 4, "y_pos": 4}]
                                                                                })
                                
                            assert response.status_code == 200
                            game_manager_mock.apilar_carta_y_ficha.assert_called_once_with(1, 1, 
                                                                                           (Ficha(x_pos=2, y_pos=2), 
                                                                                            Ficha(x_pos=4, y_pos=4)))


def test_use_mov_card_invalid_move():
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)) as mock_get_jugador:
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio,
                                                                                partida_id=1, jugador_id=1)):
                with patch('src.main.get_jugador_en_turno', return_value= mock_get_jugador.return_value):
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

def test_use_mov_card_invalid_card():
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)) as mock_get_jugador:
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio,
                                                                                partida_id=1, jugador_id=2)) as mock_get_carta:
                with patch('src.main.get_jugador_en_turno', return_value= mock_get_jugador.return_value):
                    with patch('src.main.is_valid_move', return_value = False):
                        with patch('src.main.movimiento_parcial', return_value = None):
                            response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                                "id_mov_card": 1,
                                                                                "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                        {"x_pos": 2, "y_pos": 3}]
                                                                                })
                                
                            assert response.status_code == 400
                            assert response.json() == {'detail': "La carta no pertenece al jugador"}
                            game_manager_mock.apilar_carta_y_ficha.assert_not_called()

                            mock_get_carta.return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                        movimiento= Move.diagonal_con_espacio,
                                                                        partida_id=2, jugador_id=1)
                            
                            response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                                "id_mov_card": 1,
                                                                                "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                        {"x_pos": 2, "y_pos": 3}]
                                                                                })
                            
                            assert response.status_code == 400
                            assert response.json() == {'detail': "La carta no pertenece a la partida"}
                            game_manager_mock.apilar_carta_y_ficha.assert_not_called()

def test_use_mov_card_invalid_player():
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)) as mock_get_jugador:
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio,
                                                                                partida_id=1, jugador_id=2)):
                with patch('src.main.get_jugador_en_turno', return_value= Jugador(id=2, partida_id= 1)):
                    with patch('src.main.is_valid_move', return_value = False):
                        with patch('src.main.movimiento_parcial', return_value = None):
                            response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                                "id_mov_card": 1,
                                                                                "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                        {"x_pos": 2, "y_pos": 3}]
                                                                                })
                                
                            assert response.status_code == 400
                            assert response.json() == {'detail': "No es turno del jugador"}
                            game_manager_mock.apilar_carta_y_ficha.assert_not_called()

def test_use_mov_card_error():
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)) as mock_get_jugador:
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio,
                                                                                partida_id=1, jugador_id=1)):
                with patch('src.main.get_jugador_en_turno', return_value= mock_get_jugador.return_value):
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

@pytest.mark.asyncio
@patch("src.main.get_valid_detected_figures")
@patch("src.main.get_color_of_ficha")
@patch("src.main.get_db")
async def test_highlight_figures(mock_get_db, mock_get_color_of_ficha, mock_get_valid_detected_figures):
    # Crear un mock de la base de datos
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    # Mockear la lista de figuras detectadas que devuelve get_valid_detected_figures
    mock_figures = [
        [(0, 0), (0, 1)],  # Figura 1
        [(1, 1), (1, 2)]   # Figura 2
    ]
    mock_get_valid_detected_figures.return_value = mock_figures

    # Mockear la respuesta de get_color_of_ficha (color para cada ficha)
    mock_get_color_of_ficha.return_value = Color.ROJO.value

    # Parámetros para la llamada al endpoint
    game_id = 1
    response = client.get(f"/game/highlight-figures?game_id={game_id}")

    # Verificar el status code
    assert response.status_code == 200

    # Verificar la estructura de la respuesta
    expected_response = [
        [
            {'x': 1, 'y': 1, 'color': Color.ROJO.value},
            {'x': 1, 'y': 2, 'color': Color.ROJO.value}
        ],
        [
            {'x': 2, 'y': 2, 'color': Color.ROJO.value},
            {'x': 2, 'y': 3, 'color': Color.ROJO.value}
        ]
    ]
    assert response.json() == expected_response

@pytest.mark.asyncio
@patch("src.main.get_valid_detected_figures")
@patch("src.main.get_db")
async def test_highlight_figures_db_error(mock_get_db, mock_get_valid_detected_figures):
    # Crear un mock de la base de datos
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    # Simular un error al obtener las figuras detectadas
    mock_get_valid_detected_figures.side_effect = Exception("Database error")

    # Parámetros para la llamada al endpoint
    game_id = 1
    response = client.get(f"/game/highlight-figures?game_id={game_id}")

    # Verificar que se devuelva un error 500
    assert response.status_code == 500

    # Verificar el contenido del mensaje de error
    assert response.json() == {"detail": "Error al obtener las figuras"}

