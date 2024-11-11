import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import OperationalError
from src.main import app 

@pytest.fixture
def client():
    return TestClient(app)

def test_get_lobbies_succes(client):
    with patch('src.db.get_db'):
        with patch('src.routers.home.list_lobbies', return_value=[]):
            response = client.get("/home/get-lobbies?username=test")

            assert response.status_code == 200
            assert response.json() == []

def test_get_lobbies_failure(client):
    with patch('src.db.get_db'):
        with patch('src.routers.home.list_lobbies', side_effect=OperationalError("Error de DB", 
                                                                        params=None, 
                                                                        orig=None)):
        
            response = client.get("/home/get-lobbies?username=test")

            assert response.status_code == 500
            assert response.json() == {"detail": "Error al obtener los lobbies."}