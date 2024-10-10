import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from src.main import app 


@pytest.fixture
def client():
    return TestClient(app)

def test_get_winner(client):
    with patch('src.main.get_jugadores') as mock_get_jugadores:
        game_id = 1
        jugadores_mock = [
            MagicMock(id=1, nombre="testwinner"),
        ]

        mock_get_jugadores.return_value = jugadores_mock

        response = client.get("/game/get-winner", params={"game_id": game_id})

        assert response.status_code == 200
        assert response.json() == {"name_player": "testwinner"}

def test_except_winner(client):
    with patch('src.main.get_jugadores') as mock_get_jugadores:
        game_id = 1
        jugadores_mock = [
            MagicMock(id=1, nombre="testwinner"),
        ]

        mock_get_jugadores.return_value = jugadores_mock
        mock_get_jugadores.side_effect = SQLAlchemyError

        response = client.get("/game/get-winner", params={"game_id": game_id})

        assert response.status_code == 500
        assert response.json() == {"detail": "Fallo en la base de datos"}
