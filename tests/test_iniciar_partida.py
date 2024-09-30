import pytest
from fastapi.testclient import TestClient
from unittest import mock
from src.main import app, get_db  # Asegúrate de importar tu app y el método get_db
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from sqlalchemy.exc import SQLAlchemyError

client = TestClient(app)

def test_start_game():
    # Mock del objeto de sesión de la base de datos
    mock_db = mock.Mock()
    
    # Define qué retornará get_db
    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db

    # Mockea las funciones que se llaman dentro de start_game
    with mock.patch("src.main.mezclar_fichas") as mock_mezclar_fichas, \
         mock.patch("src.main.mezclar_cartas_movimiento") as mock_mezclar_cartas, \
         mock.patch("src.main.mezclar_figuras") as mock_mezclar_figuras, \
         mock.patch("src.main.asignar_turnos") as mock_asignar_turnos, \
         mock.patch("src.main.list_lobbies_ws") as mock_list_lobbies_ws, \
         mock.patch("src.main.get_Partida") as mock_get_partida:
        
        # Configura el mock para get_Partida
        mock_partida = mock.Mock()
        mock_partida.partida_iniciada = False
        mock_get_partida.return_value = mock_partida
        
        # Llama al endpoint
        response = client.put("/game/start-game", json={"game_id": 1})

        # Asegúrate de que la respuesta sea la esperada
        assert response.status_code == 200
        assert response.json() == {"id_game": 1, "iniciada": True}

        # Verifica que las funciones fueron llamadas correctamente
        mock_mezclar_fichas.assert_called_once_with(mock_db, 1)
        mock_mezclar_cartas.assert_called_once_with(mock_db, 1)
        mock_mezclar_figuras.assert_called_once_with(1, mock_db)
        mock_asignar_turnos.assert_called_once_with(1, mock_db)

    # Restablece las dependencias
    app.dependency_overrides.clear()

def test_start_game_exception():
    # Mock del objeto de sesión de la base de datos
    mock_db = mock.Mock()
    
    # Define qué retornará get_db
    async def mock_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = mock_get_db

    # Mockea las funciones que se llaman dentro de start_game
    with mock.patch("src.main.mezclar_fichas") as mock_mezclar_fichas, \
         mock.patch("src.main.mezclar_cartas_movimiento") as mock_mezclar_cartas, \
         mock.patch("src.main.mezclar_figuras") as mock_mezclar_figuras, \
         mock.patch("src.main.asignar_turnos") as mock_asignar_turnos, \
         mock.patch("src.main.list_lobbies_ws") as mock_list_lobbies_ws, \
         mock.patch("src.main.get_Partida") as mock_get_partida:

        # Simula que se lanza una excepción en mezclar_fichas
        mock_get_partida.side_effect = SQLAlchemyError()
        
        # Llama al endpoint
        response = client.put("/game/start-game", json={"game_id": 1})

        # Asegúrate de que la respuesta sea un error 500
        assert response.status_code == 500
        assert response.json() == {"detail": "Fallo en la base de datos"}

    # Restablece las dependencias
    app.dependency_overrides.clear()

    
