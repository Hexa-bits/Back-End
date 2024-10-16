import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.models.utils import Coords
from src.main import app, lista_patrones
from sqlalchemy.exc import SQLAlchemyError
from src.models.fichas_cajon import Color

client = TestClient(app)

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

@pytest.mark.asyncio
@patch("src.main.get_Jugador")
@patch("src.main.get_Partida")
@patch("src.main.game_manager")
@patch("src.main.cancelar_movimiento")
@patch("src.main.get_db")
async def test_cancelar_mov_OK(mock_get_db, mock_cancel_movimiento,
                                mock_manager, mock_get_partida, mock_get_jugador):
    #Inicializo elementos para la prueba
    mock_partida = MagicMock(id=1, jugador_en_turno=0, partida_empezada=True)
    mock_jugador = MagicMock(id=1, turno=0, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = mock_partida
    mock_get_jugador.return_value = mock_jugador
    mock_cancel_movimiento.return_value = None
    
    mock_manager.top_tupla_carta_y_fichas.return_value = (1, ((1, 1), (2, 2)))
    mock_manager.desapilar_carta_y_ficha.return_value = None

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_partida.assert_called_once_with(1, ANY)
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_manager.top_tupla_carta_y_fichas.assert_called_once_with(game_id=1)
    mock_cancel_movimiento.assert_called_with (partida=mock_partida,
                                              jugador=mock_jugador, 
                                              mov=1,
                                              coords=(Coords(x=1, y=1), Coords(x=2, y=2)), 
                                              db=ANY)
    mock_manager.desapilar_carta_y_ficha.assert_called_once_with(game_id=1)

    assert response.status_code == 204

@pytest.mark.asyncio
@patch("src.main.get_Jugador")
@patch("src.main.get_Partida")
@patch("src.main.game_manager")
@patch("src.main.cancelar_movimiento")
@patch("src.main.get_db")
async def test_cancelar_mov_not_mov_parcial(mock_get_db, mock_cancel_movimiento,
                                          mock_manager, mock_get_partida, mock_get_jugador):
    #Inicializo elementos para la prueba
    mock_partida = MagicMock(id=1, jugador_en_turno=0, partida_empezada=True)
    mock_jugador = MagicMock(id=1, turno=0, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = mock_partida
    mock_get_jugador.return_value = mock_jugador
    mock_cancel_movimiento.return_value = None
    
    mock_manager.top_tupla_carta_y_fichas.return_value = None
    mock_manager.desapilar_carta_y_ficha.return_value = None

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_partida.assert_called_once_with(1, ANY)
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_manager.top_tupla_carta_y_fichas.assert_called_once_with(game_id=1)
    mock_cancel_movimiento.assert_not_called()
    mock_manager.desapilar_carta_y_ficha.assert_not_called()

    assert response.status_code == 404
    assert response.json() == {"detail": "No hay movimientos que deshacer"}

@pytest.mark.asyncio
@patch("src.main.get_Jugador")
@patch("src.main.get_Partida")
@patch("src.main.game_manager")
@patch("src.main.cancelar_movimiento")
@patch("src.main.get_db")
async def test_cancelar_mov_not_jugador(mock_get_db, mock_cancel_movimiento,
                                        mock_manager, mock_get_partida, mock_get_jugador):
    #Inicializo elementos para la prueba
    mock_jugador = None

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.return_value = mock_jugador

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_get_partida.assert_not_called()
    mock_manager.top_tupla_carta_y_fichas.assert_not_called()
    mock_cancel_movimiento.assert_not_called()
    mock_manager.desapilar_carta_y_ficha.assert_not_called()

    assert response.status_code == 404
    assert response.json() == {"detail": f'No existe el jugador: {config["player_id"]}'}


@pytest.mark.asyncio
@patch("src.main.get_Jugador")
@patch("src.main.get_Partida")
@patch("src.main.game_manager")
@patch("src.main.cancelar_movimiento")
@patch("src.main.get_db")
async def test_cancelar_mov_sql_error(mock_get_db, mock_cancel_movimiento,
                                        mock_manager, mock_get_partida, mock_get_jugador):

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.side_effect=SQLAlchemyError()

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_get_partida.assert_not_called()
    mock_manager.top_tupla_carta_y_fichas.assert_not_called()
    mock_cancel_movimiento.assert_not_called()
    mock_manager.desapilar_carta_y_ficha.assert_not_called()

    assert response.status_code == 500
    assert response.json() == {"detail": "Fallo en la base de datos"}

