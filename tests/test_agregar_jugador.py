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
from sqlalchemy.orm import Session
from src.main import app 

@pytest.fixture
def client():
    return TestClient(app)

def test_join_success(client):
    # Mock de la sesión de la base de datos
    player_mock = MagicMock(id=1, nombre="testjoin")
    game_mock = MagicMock(id=1, game_name="partida", max_players=4, partida_iniciada=False)
    
    with patch('src.db.get_db', return_value=MagicMock(spec=Session)), \
        patch('src.routers.game.add_player_game', return_value=player_mock), \
        patch('src.routers.game.num_players_in_game', return_value=2), \
        patch('src.routers.game.block_manager.add_player', return_value= None), \
        patch('src.routers.game.get_Partida', return_value=game_mock):
        response = client.post("/game/join", json={"player_id": player_mock.id , "game_id": 1})

        print(response.json())
        assert response.status_code == 200
        assert response.json() == {"player_id": player_mock.id,
                            "game_id": 1}

def test_join_many_players(client):
    players_mock = [
                    MagicMock(id=1, nombre="testjoins"),
                    MagicMock(id=2, nombre="testjoins"),
                    MagicMock(id=3, nombre="testjoins"),
                    ]
    
    game_mock = MagicMock(id=1, game_name="partida", max_players=4, partida_iniciada=False)
    
    with patch('src.db.get_db', return_value=MagicMock(spec=Session)), \
        patch('src.routers.game.add_player_game') as mock_player, \
        patch('src.routers.game.num_players_in_game'), \
        patch('src.routers.game.block_manager.add_player', return_value= None), \
        patch('src.routers.game.get_Partida', return_value=game_mock):

        mock_player.return_value = players_mock[0]
        response = client.post("/game/join", json={"player_id": players_mock[0].id , "game_id": game_mock.id})
        assert response.json() == {"player_id": players_mock[0].id, "game_id": game_mock.id}

        mock_player.return_value = players_mock[1]
        response = client.post("/game/join", json={"player_id": players_mock[1].id , "game_id": game_mock.id})
        assert response.json() == {"player_id": players_mock[1].id, "game_id": game_mock.id}

        mock_player.return_value = players_mock[2]
        response = client.post("/game/join", json={"player_id": players_mock[2].id , "game_id": game_mock.id})
        assert response.json() == {"player_id": players_mock[2].id, "game_id": game_mock.id}


def test_join_failure(client):
    player_mock = MagicMock(id=1, nombre="testjoin")
    game_mock = MagicMock(id=1, game_name="partida", max_players=4, partida_iniciada=False)

    with patch('src.db.get_db', return_value=MagicMock(spec=Session)), \
         patch('src.routers.game.add_player_game', side_effect=SQLAlchemyError()), \
         patch('src.routers.game.num_players_in_game'), \
         patch('src.routers.game.get_Partida', return_value=game_mock):
        
        response = client.post("/game/join", json={"player_id": player_mock.id , "game_id": 1})

        assert response.status_code == 500
        assert response.json() == {"detail": "Error al unirse a partida"}

def test_join_full_game(client):
    player_mock = MagicMock(id=1, nombre="testjoin")
    game_mock = MagicMock(id=1, game_name="partida", max_players=4, partida_iniciada=False)

    with patch('src.db.get_db', return_value=MagicMock(spec=Session)), \
         patch('src.routers.game.num_players_in_game', return_value=4), \
         patch('src.routers.game.get_Partida', return_value=game_mock):
        
        response = client.post("/game/join", json={"player_id": player_mock.id , "game_id": 1})

        assert response.status_code == 400
        assert response.json() == {"detail": "No se aceptan más jugadores"}

def test_player_not_found(client):
    game_mock = MagicMock(id=1, game_name="partida", max_players=4, partida_iniciada=False)

    with patch('src.routers.game.add_player_game', return_value= None), \
         patch('src.routers.game.get_Partida', return_value=game_mock):
        
        response = client.post("/game/join", json={"player_id": 1 , "game_id": 1})

        assert response.status_code == 404
        assert response.json() == {"detail": "El jugador no existe"}

def test_game_not_found(client):
    player_mock = MagicMock(id=1, nombre="testjoin")

    with patch('src.routers.game.add_player_game', return_value=player_mock), \
         patch('src.routers.game.get_Partida', return_value= None):

        response = client.post("/game/join", json={"player_id": 1 , "game_id": 1})

        assert response.status_code == 404
        assert response.json() == {"detail": "La partida no existe"}