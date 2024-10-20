import pytest
from fastapi.testclient import TestClient
from src.main import app, lista_patrones
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound
from unittest.mock import MagicMock, patch, ANY
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

def test_use_mov_card_invalid_player_or_not_in_hand():
    with patch('src.main.game_manager') as game_manager_mock:
        with patch('src.main.get_Jugador', return_value = Jugador(id=1, partida_id= 1)) as mock_get_jugador:
            with patch('src.main.get_CartaMovimiento', return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                                                movimiento= Move.diagonal_con_espacio,
                                                                                partida_id=1, jugador_id=2)) as mock_get_carta:
                with patch('src.main.get_jugador_en_turno', return_value= Jugador(id=2, partida_id= 1)) as mock_get_jugador_turno:
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

                            mock_get_carta.return_value = MovementCard(id=1, estado= CardStateMov.descartada, 
                                                                        movimiento= Move.diagonal_con_espacio,
                                                                        partida_id=1, jugador_id=2)
                            
                            mock_get_jugador.return_value = mock_get_jugador_turno.return_value 

                            response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                                                "id_mov_card": 1,
                                                                                "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                                        {"x_pos": 2, "y_pos": 3}]
                                                                                })
                                
                            assert response.status_code == 400
                            assert response.json() == {'detail': "La carta no está en mano"}
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


@patch("src.main.get_jugador_sin_cartas")
@patch("src.main.get_jugadores")
@patch("src.main.get_db")
def test_get_winner_OK_sin_cartas(mock_get_db, mock_get_jugadores, 
                                 mock_get_jugador_sin_cartas):
    
    mock_get_db.return_value = MagicMock(spec=Session)

    game_id = 1
    jugadores_mock = [
                      MagicMock(id=1, nombre="testwinner", partida_id=1),
                      MagicMock(id=2, nombre="testlosser", partida_id=1)
                     ]

    mock_get_jugadores.return_value = jugadores_mock
    mock_get_jugador_sin_cartas.return_value = jugadores_mock[0]

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_jugadores.assert_called_once_with(game_id, ANY)
    mock_get_jugador_sin_cartas.assert_called_once_with(game_id, ANY)
    assert response.status_code == 200
    assert response.json() == {"name_player": "testwinner"}


@patch("src.main.get_jugador_sin_cartas")
@patch("src.main.get_jugadores")
@patch("src.main.get_db")
def test_get_winner_OK_abandonar(mock_get_db, mock_get_jugadores, 
                                 mock_get_jugador_sin_cartas):
    
    mock_get_db.return_value = MagicMock(spec=Session)

    game_id = 1
    jugadores_mock = [MagicMock(id=1, nombre="testwinner", partida_id=1)]

    mock_get_jugadores.return_value = jugadores_mock
    mock_get_jugador_sin_cartas.return_value = None

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_jugadores.assert_called_once_with(game_id, ANY)
    mock_get_jugador_sin_cartas.assert_called_once_with(game_id, ANY)
    assert response.status_code == 200
    assert response.json() == {"name_player": "testwinner"}


@patch("src.main.get_jugador_sin_cartas")
@patch("src.main.get_jugadores")
@patch("src.main.get_db")
def test_except_winner_abandonar(mock_get_db, mock_get_jugadores, 
                                mock_get_jugador_sin_cartas):
    
    mock_get_db.return_value = MagicMock(spec=Session)
    
    game_id = 1

    mock_get_jugador_sin_cartas.return_value = None
    mock_get_jugadores.side_effect = SQLAlchemyError()

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_jugadores.assert_called_once_with(game_id, ANY)
    mock_get_jugador_sin_cartas.assert_not_called()
    assert response.status_code == 500
    assert response.json() == {"detail": "Fallo en la base de datos"}


@patch("src.main.get_jugador_sin_cartas")
@patch("src.main.get_jugadores")
@patch("src.main.get_db")
def test_except_winner_sin_cartas(mock_get_db, mock_get_jugadores, 
                                mock_get_jugador_sin_cartas):
    
    mock_get_db.return_value = MagicMock(spec=Session)
    
    game_id = 1
    jugadores_mock = [
                      MagicMock(id=1, nombre="testlosser", partida_id=1),
                      MagicMock(id=2, nombre="testlosser", partida_id=1)
                     ]

    mock_get_jugadores.return_value = jugadores_mock
    #Encuentra más de uno (.one garantiza esto y arroja excep)
    mock_get_jugador_sin_cartas.side_effect = MultipleResultsFound()

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_jugadores.assert_called_once_with(game_id, ANY)
    mock_get_jugador_sin_cartas.assert_called_once_with(game_id, ANY)
    assert response.status_code == 500
    assert response.json() == {"detail": "Fallo en la base de datos"}


@patch("src.main.get_jugador_sin_cartas")
@patch("src.main.get_jugadores")
@patch("src.main.get_db")
def test_winner_BAD_request(mock_get_db, mock_get_jugadores, 
                            mock_get_jugador_sin_cartas):

    mock_get_db.return_value = MagicMock(spec=Session)
    
    game_id = 1
    jugadores_mock = [
                        MagicMock(id=1, nombre="testlosser1", partida_id=1),
                        MagicMock(id=2, nombre="testlosser2", partida_id=1)
                     ]
    
    mock_get_jugadores.return_value = jugadores_mock
    mock_get_jugador_sin_cartas.return_value = None

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_jugadores.assert_called_once_with(game_id, ANY)
    mock_get_jugador_sin_cartas.assert_called_once_with(game_id, ANY)
    assert response.status_code == 400
    assert response.json() == {"detail": f"No hay ganador aún en partida: {game_id}"}