import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import OperationalError
from src.main import app 

@pytest.fixture
def client():
    return TestClient(app)

def test_login_success(client):
    # Mock de la sesión de la base de datos
    with patch('src.main.get_db'):
        response = client.post("/login", json={"username": "testuser"})

        assert response.status_code == 201
        assert response.json() != {"id": None}

def test_login_failure(client):
    with patch('src.main.get_db'):
        with patch('src.main.add_player', side_effect=OperationalError("Error de DB", 
                                                                        params=None, 
                                                                        orig=None)):
        
            response = client.post("/login", json={"username": "testuser"})

            assert response.status_code == 500
            assert response.json() == {"detail": "Error al crear el usuario."}
