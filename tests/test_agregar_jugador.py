import pytest
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.models.jugadores import Jugador
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, ANY
from sqlalchemy.exc import OperationalError
import pdb
from src.main import app 

@pytest.fixture
def client():
    return TestClient(app)

def test_join_success(client):
    # Mock de la sesión de la base de datos
    with patch('src.main.get_db'): 
        player_mock = MagicMock()
        player_mock.return_value = Jugador(id= 1, nombre= "testjoin")
        game_mock = MagicMock()
        game_mock.return_value = Partida(id= 1, game_name="partida", max_players= 4)
        
        with patch('src.main.add_player_game'):
            response = client.post("/game/join", json={"player_id": player_mock.return_value.id , "game_id": game_mock.return_value.id})
  
            assert response.status_code == 200
            assert response.json() == {"player_id": player_mock.return_value.id,
                                    "game_id": game_mock.return_value.id}
            
def check_post_method(client: client, player_mock_id: int, game_id: int):
    response = client.post("/game/join", json={"player_id": player_mock_id , "game_id": game_id})
    assert response.status_code == 200
    assert response.json() == {"player_id": player_mock_id,
                                "game_id": game_id} 

def test_join_many_players(client):
    with patch('src.main.add_player_game') as mock_jugador:
        mock_jugador.return_value = Jugador(id= 1, nombre= "testjoins")
        mock_jugador.return_value.partida_id = 1
        response = client.post("/game/join", json={"player_id": 1 , "game_id": 1})
        assert response.json() == {"player_id": 1, "game_id": 1}

        mock_jugador.return_value = Jugador(id= 2, nombre= "testjoins")
        mock_jugador.return_value.partida_id = 1
        response1 = client.post("/game/join", json={"player_id": 2 , "game_id": 1})
        assert response1.json() == {"player_id": 2, "game_id": 1}

        mock_jugador.return_value = Jugador(id= 3, nombre= "testjoins")
        mock_jugador.return_value.partida_id = 1
        response1 = client.post("/game/join", json={"player_id": 2 , "game_id": 1})
        assert response1.json() == {"player_id": 3, "game_id": 1}

def test_login_failure(client):
    with patch('src.main.get_db'):
        player_mock = MagicMock()
        player_mock.return_value = Jugador(id= 1, nombre= "testjoin")
        game_mock = MagicMock()
        game_mock.return_value = Partida(id= 1, game_name="partida", max_players= 4)

        with patch('src.main.add_player_game', side_effect=Exception()):
        
            response = client.post("/game/join", json={"player_id": player_mock.return_value.id , "game_id": game_mock.return_value.id})

            assert response.status_code == 500
            assert response.json() == {"detail": "Error al unirse a partida"}
