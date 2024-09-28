from sqlalchemy.exc import OperationalError

from src.main import app
import pytest

from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .test_helpers import mock_add_partida, cheq_entity
from src.models.jugadores import Jugador
from src.models.partida import Partida


from sqlalchemy.exc import IntegrityError




from src.models.inputs_front import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from unittest.mock import ANY
import json

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
