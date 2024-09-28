import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import OperationalError
from src.main import app 

@pytest.fixture
def client():
    return TestClient(app)


def test_get_lobby_info_success(client):
    with patch('src.main.get_db'):
        
        with patch('src.main.get_lobby', return_value={"game_name": "Juego1", 
                                                        "max_players": 4, 
                                                        "name_players": ["player1", "player2"]}):
            
            response = client.get("/home/lobby?game_id=1")

            assert response.status_code == 200
            assert response.json() != {"game_name": None, "max_players": None, "name_players": None}

def test_get_lobby_info_failure(client):
    with patch('src.main.get_db'):
        with patch('src.main.get_lobby', side_effect=OperationalError("Error de DB", 
                                                                        params=None, 
                                                                        orig=None)):
            response = client.get("/home/lobby?game_id=1")
            assert response.status_code == 500
            assert response.json() == {"detail": "Error al obtener la partida"}