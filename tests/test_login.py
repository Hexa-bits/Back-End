from unittest.mock import Mock, MagicMock
from src.main import login, app
from tests.test_helpers import test_db
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.jugadores import Jugador
from src.models.cartafigura import pictureCard
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import pytest


client = TestClient(app)


@pytest.fixture
def mock_db_session(monkeypatch):
    # Crear un mock de la función get_db
    mock_db = test_db()
    monkeypatch.setattr("src.main.get_db", lambda: mock_db)  # Reemplaza con la ruta correcta de tu aplicación
    return mock_db

def test_login_success(client, mock_db_session):
    response = client.post("/login", json={"username": "test_user"})
    
    assert response.status_code == 201
    assert response.json() == {"id": 1}  # Asegúrate de que el ID simulado sea el correcto

def test_login_db_error(client, mock_db_session):
    # Modificar el método commit para lanzar una excepción
    def raise_exception():
        raise Exception("DB Error")
    
    mock_db_session.commit = raise_exception

    response = client.post("/login", json={"username": "test_user"})
    
    assert response.status_code == 500
    assert response.json() == {"detail": "Error al crear el usuario."}
