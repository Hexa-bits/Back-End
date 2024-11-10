import pytest
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.models.jugadores import Jugador
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, ANY
from sqlalchemy.exc import SQLAlchemyError
import pdb
from src.main import app 

@pytest.fixture
def client():
    return TestClient(app)

def test_join_success(client):
    # Mock de la sesión de la base de datos
    with patch('src.db.get_db'): 
        player_mock = MagicMock()
        player_mock.return_value = Jugador(id= 1, nombre= "testjoin")
        
        with patch('src.routers.game.add_player_game'):
            with patch('src.routers.game.get_Partida', return_value= Partida(id= 1, game_name="partida", max_players= 4)):
                response = client.post("/game/join", json={"player_id": player_mock.return_value.id , "game_id": 1})
  
                assert response.status_code == 200
                assert response.json() == {"player_id": player_mock.return_value.id,
                                    "game_id": 1}

def test_join_many_players(client):
    with patch('src.routers.game.add_player_game') as mock_jugador:
        with patch('src.routers.game.get_Partida', return_value= Partida(id= 1, game_name="partida", max_players= 4)):
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

def test_join_failure(client):
    with patch('src.db.get_db'):
        player_mock = MagicMock()
        player_mock.return_value = Jugador(id= 1, nombre= "testjoin")

        with patch('src.routers.game.add_player_game', side_effect=SQLAlchemyError()):
            with patch('src.routers.game.get_Partida', return_value= Partida(id= 1, game_name="partida", max_players= 4)):
        
                response = client.post("/game/join", json={"player_id": player_mock.return_value.id , "game_id": 1})

                assert response.status_code == 500
                assert response.json() == {"detail": "Error al unirse a partida"}

def test_player_not_found(client):
    with patch('src.routers.game.add_player_game', return_value= None):
        with patch('src.routers.game.get_Partida', return_value= Partida(id= 1, game_name="partida", max_players= 4)):
            response = client.post("/game/join", json={"player_id": 1 , "game_id": 1})

            assert response.status_code == 404
            assert response.json() == {"detail": "El jugador no existe"}

def test_game_not_found(client):
    with patch('src.routers.game.add_player_game', return_value= Jugador(id= 1, nombre= "test")):
        with patch('src.routers.game.get_Partida', return_value= None):
            response = client.post("/game/join", json={"player_id": 1 , "game_id": 1})

            assert response.status_code == 404
            assert response.json() == {"detail": "La partida no existe"}