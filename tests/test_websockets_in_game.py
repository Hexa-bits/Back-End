import asyncio
import json
import pytest
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.color_enum import Color
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.models.cartamovimiento import CardStateMov
from src.models.cartafigura import CardState
from src.main import app
from src.ws_manager import CANCEL_LOBBY, JOIN_GAME, GET_INFO_PLAYERS, GET_BOARD, GET_CARTAS_FIG, GET_CARTAS_MOV
from src.routers.game import ws_manager, block_manager
from unittest.mock import MagicMock, patch

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

mock_partida = MagicMock()
mock_partida.id = 1
mock_partida.winner_id = None
mock_partida.partida_iniciada = False
mock_partida.password = None

mock_jugador = MagicMock()
mock_jugador.id = 1
mock_jugador.nombre = "testws"
mock_jugador.partida_id = mock_partida.id
mock_jugador.es_anfitrion = True

mock_jugadores = MagicMock()
mock_jugadores.return_value = [MagicMock(id=2, nombre="test", partida_id=1), 
                               MagicMock(id=3, nombre="test", partida_id=1)]


@pytest.mark.asyncio
async def test_websocket_connection(client):
    # Comprobar cuántas conexiones activas hay antes de la conexión
    initial_connections = len(ws_manager.active_connections)

    #Simulo una conexión al WebSocket
    with client.websocket_connect("/game?game_id=1") as websocket:
        # Verificar que el WebSocket se conectó correctamente
        assert websocket is not None

        # Verificar que la cantidad de conexiones activas aumentó
        assert len(ws_manager.active_connections) == initial_connections + 1  
        assert len(ws_manager.active_connections.get(1)) == 1    
    
    await asyncio.sleep(0.1)
    # Después de cerrar la conexión, verificar que la cantidad de conexiones activas disminuyó
    assert len(ws_manager.active_connections) == initial_connections


@pytest.mark.asyncio
async def test_websocket_connections(client):
    initial_connections = len(ws_manager.active_connections)
    assert initial_connections == 0
    
    with client.websocket_connect("/game?game_id=1"), \
         client.websocket_connect("/game?game_id=1"), \
         client.websocket_connect("/game?game_id=2"):
                
        assert len(ws_manager.active_connections) == initial_connections + 2  
        assert len(ws_manager.active_connections.get(1)) == 2
        assert len(ws_manager.active_connections.get(2)) == 1    
    
    await asyncio.sleep(0.1)
    
    assert len(ws_manager.active_connections) == initial_connections


@pytest.mark.asyncio
async def test_websocket_broadcast_turno_siguiente(client):
    # Simular que un cliente se conecta al WebSocket
    with client.websocket_connect("/game?game_id=1") as websocket1, \
         client.websocket_connect("/game?game_id=1") as websocket2:

        assert len(ws_manager.active_connections) == 1  
        assert len(ws_manager.active_connections.get(1)) == 2 
        
        with patch("src.routers.game.get_current_turn_player", return_value = mock_jugador), \
             patch("src.routers.game.game_manager.is_board_parcial", return_value=False), \
             patch('src.routers.game.terminar_turno', return_value = {"id_player": 2 ,
                                                                "name_player": "testuser"}), \
            patch('src.routers.game.repartir_cartas', return_value= None), \
            patch("src.routers.game.game_manager.set_player_in_turn_id"), \
            patch("src.routers.game.block_manager.is_blocked", return_value= False):
            # Simular una petición HTTP para obtener el siguiente turno
            response = client.put("/game/end-turn", json={"game_id": 1})
            # Esperar a que los lobbies se envíen a los clientes WebSocket conectados
            assert response.status_code == 200
            await asyncio.sleep(0.1)
            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == "Terminó turno"
            assert mensaje1 == "Terminó turno"

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == "{'type': 'log', 'data': {'player_name': 'testws', 'event': 'Terminó el turno'}}"
            assert mensaje1 == mensaje2


@pytest.mark.asyncio
async def test_websocket_broadcast_ganador(client):
    partida_mock = MagicMock()
    partida_mock.return_value = Partida(id=1, game_name = "testWsWinner", partida_iniciada= True)
    jugadores_mock = [
        MagicMock(id=1, nombre="testloser", partida_id= 1),
        MagicMock(id=2, nombre="testwinner", partida_id= 1)
    ]
    
    with client.websocket_connect("/game?game_id=1") as websocket2:
        with client.websocket_connect("/game?game_id=1") as websocket1:
            assert len(ws_manager.active_connections) == 1  
            assert len(ws_manager.active_connections.get(1)) == 2 
            
            with patch('src.routers.game.get_Jugador', return_value = jugadores_mock[0]), \
                 patch('src.routers.game.get_Partida', return_value = partida_mock.return_value), \
                 patch('src.routers.game.get_players', side_effect=[jugadores_mock, [jugadores_mock.pop(0)]]), \
                 patch('src.routers.game.game_manager.delete_game') as mock_game_manager, \
                 patch('src.routers.game.block_manager.delete_game') as mock_block_manager, \
                 patch('src.routers.game.delete_player', return_value = None):
                            
                response = client.put("/game/leave", json={"id_user": 1, "game_id": 1})
                assert response.status_code == 204
                mock_game_manager.assert_called_once_with(1)
                mock_block_manager.assert_called_once_with(1)

        # se cierra la conexion websocket1 simulando que el jugador abandono
        await asyncio.sleep(0.1)
        assert websocket2.receive_text() == "Actualizar cartas de otros jugadores"
        await asyncio.sleep(0.1)
        assert websocket2.receive_text() == "{'type': 'log', 'data': {'player_name': 'testloser', 'event': 'Abandonó la partida'}}"
        await asyncio.sleep(0.1)
        assert websocket2.receive_text() == "Hay Ganador"
        assert len(ws_manager.active_connections.get(1)) == 1
        #Borre la verificación posterior porque ya se hace en test_routers.game

    await asyncio.sleep(0.1)
    
    assert len(ws_manager.active_connections) == 0


@pytest.mark.asyncio
async def test_websocket_broadcast_games_join(client):
    with client.websocket_connect("/game?game_id=1") as websocket1, \
        client.websocket_connect("/game?game_id=1") as websocket2:
        with patch("src.routers.game.add_player_game", return_value=mock_jugador) as mock_add_partida, \
            patch("src.routers.game.get_Jugador", return_value=mock_jugador), \
            patch("src.routers.game.is_name_in_game", return_value=False), \
            patch("src.routers.game.get_Partida", return_value=mock_partida) as mock_get_partida, \
            patch("src.routers.game.num_players_in_game", return_value= 2), \
            patch("src.routers.game.block_manager.add_player", return_value= False):
            config = {"player_id": 1 , "game_id": 1, "game_password": ""}
            mock_add_partida.return_value = mock_jugador

            response = client.post("/game/join", json=config)
            assert response.status_code == 200
            lobbies1 = websocket1.receive_text()
            lobbies2 = websocket2.receive_text()

            assert lobbies1 == JOIN_GAME
            assert lobbies1 == lobbies2


@pytest.mark.asyncio
async def test_websocket_broadcast_games_leave(client):
    with client.websocket_connect("/game?game_id=1") as websocket1, \
         client.websocket_connect("/game?game_id=1") as websocket2:

        with patch("src.routers.game.get_Jugador", return_value=mock_jugador) as mock_get_jugador, \
             patch("src.routers.game.get_Partida", return_value=mock_partida) as mock_get_partida, \
             patch("src.routers.game.delete_player"), \
             patch("src.routers.game.get_players", return_value = mock_jugadores), \
             patch("src.routers.game.delete_players_lobby"):
            
            info_leave = {"id_user": 1, "game_id": 1}

            response = client.put("/game/leave", json=info_leave)

            assert response.status_code == 204

            lobbies1 = websocket1.receive_text()
            lobbies2 = websocket2.receive_text()

            assert lobbies1 == CANCEL_LOBBY
            assert lobbies1 == lobbies2

            mock_get_partida.return_value.partida_iniciada = True

            response = client.put("/game/leave", json=info_leave)

            lobbies1 = websocket1.receive_text()
            lobbies2 = websocket2.receive_text()

            assert lobbies1 == GET_INFO_PLAYERS
            assert lobbies1 == lobbies2

            await asyncio.sleep(0.1)

            lobbies1 = websocket1.receive_text()
            lobbies2 = websocket2.receive_text()

            assert lobbies1 == "{'type': 'log', 'data': {'player_name': 'testws', 'event': 'Abandonó la partida'}}"
            assert lobbies1 == lobbies2               

@pytest.mark.asyncio
async def test_broadcast_message_to_other_websockets(client):
    with client.websocket_connect("/game?game_id=1") as websocket_1, \
            client.websocket_connect("/game?game_id=1") as websocket_2, \
            client.websocket_connect("/game?game_id=1") as websocket_3:
        
        # Verifica que los WebSockets están conectados
        assert websocket_1 is not None
        assert websocket_2 is not None
        assert websocket_3 is not None
        
        # Simulo un mensaje a enviar
        response = {
            "type": "message",
            "data": {
                "msg": "Hola",
                "player_name": "Pepe"
            }
        }
        response_text = json.dumps(response)
        
        # Envío el mensaje usando ws_manager a todos los de game_id 1
        await ws_manager.send_message_game_id(game_id=1, message=response_text)
        
        # Espero para que los mensajes sean enviados
        await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_websocket_broadcast_use_mov_card(client):
    with client.websocket_connect("/game?game_id=1") as websocket1, \
         client.websocket_connect("/game?game_id=1") as websocket2:

        with patch("src.routers.game.get_Jugador", return_value=mock_jugador), \
             patch("src.routers.game.get_CartaMovimiento", return_value=MagicMock(id = 1, estado=CardStateMov.mano, 
                                                                          jugador_id=1, partida_id=1)), \
             patch("src.routers.game.get_current_turn_player", return_value=mock_jugador), \
             patch("src.routers.game.is_valid_move", return_value = True), \
             patch("src.routers.game.movimiento_parcial"), \
             patch("src.routers.game.game_manager"):
            
            info = {"player_id": 1, "id_mov_card": 1, "fichas": [{"x_pos": 1, "y_pos": 1}, {"x_pos": 1, "y_pos": 1}]}

            response = client.put("/game/use-mov-card", json=info)

            assert response.status_code == 200

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == GET_BOARD
            assert mensaje1 == mensaje2

            await asyncio.sleep(0.1)

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == GET_CARTAS_MOV
            assert mensaje1 == mensaje2

            await asyncio.sleep(0.1)

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == "{'type': 'log', 'data': {'player_name': 'testws', 'event': 'Hizo un movimiento'}}"
            assert mensaje1 == mensaje2


@pytest.mark.asyncio
async def test_websocket_broadcast_unlock_fig_card(client):
    with client.websocket_connect("/game?game_id=1") as websocket1, \
         client.websocket_connect("/game?game_id=1") as websocket2:

        with patch("src.routers.game.get_Jugador", return_value=mock_jugador), \
             patch("src.routers.game.get_CartaFigura", return_value=MagicMock(id = 1, estado=CardState.mano, 
                                                                          jugador_id=1, partida_id=1, blocked=False)), \
             patch("src.routers.game.get_Partida", return_value= mock_partida), \
             patch("src.routers.game.get_current_turn_player", return_value=mock_jugador), \
             patch("src.routers.game.get_color_of_box_card", return_value=Color.ROJO), \
             patch("src.routers.game.is_valid_picture_card", return_value = True), \
             patch("src.routers.game.descartar_carta_figura"), \
             patch("src.routers.game.get_jugador_sin_cartas", return_value=None), \
             patch("src.routers.game.block_manager.is_blocked", return_value=True), \
             patch("src.routers.game.block_manager.get_blocked_card_id", return_value=1), \
             patch("src.routers.game.block_manager.delete_other_card"), \
             patch("src.routers.game.block_manager.can_delete_blocked_card", side_effect=[False, True]), \
             patch("src.routers.game.unlock_player_figure_card"), \
             patch("src.routers.game.game_manager"),\
             patch("src.routers.game.get_tablero", return_value= MagicMock(color_prohibido=Color.VERDE)):
            
            info = {"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}, {"x_pos": 1, "y_pos": 1}]}

            response = client.put("/game/use-fig-card", json=info)

            assert response.status_code == 200

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == "{'type': 'log', 'data': {'player_name': 'testws', 'event': 'Desbloqueó una carta de figura'}}"
            assert mensaje1 == mensaje2

            await asyncio.sleep(0.1)

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == GET_CARTAS_FIG
            assert mensaje1 == mensaje2

            await asyncio.sleep(0.1)

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == GET_BOARD
            assert mensaje1 == mensaje2

@pytest.mark.asyncio
async def test_websocket_broadcast_use_fig_card(client):
    with client.websocket_connect("/game?game_id=1") as websocket1, \
         client.websocket_connect("/game?game_id=1") as websocket2:

        with patch("src.routers.game.get_Jugador", return_value=mock_jugador), \
             patch("src.routers.game.get_CartaFigura", return_value=MagicMock(id = 1, estado=CardState.mano, 
                                                                          jugador_id=1, partida_id=1, blocked=False)), \
             patch("src.routers.game.get_Partida", return_value= mock_partida), \
             patch("src.routers.game.get_current_turn_player", return_value=mock_jugador), \
             patch("src.routers.game.get_color_of_box_card", return_value=Color.ROJO), \
             patch("src.routers.game.is_valid_picture_card", return_value = True), \
             patch("src.routers.game.descartar_carta_figura"), \
             patch("src.routers.game.get_jugador_sin_cartas", return_value=None), \
             patch("src.routers.game.block_manager.is_blocked", return_value=False), \
             patch("src.routers.game.game_manager"),\
             patch("src.routers.game.get_tablero", return_value= MagicMock(color_prohibido=Color.VERDE)):
            
            info = {"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}, {"x_pos": 1, "y_pos": 1}]}

            response = client.put("/game/use-fig-card", json=info)

            assert response.status_code == 200

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == "{'type': 'log', 'data': {'player_name': 'testws', 'event': 'Descartó una carta de figura'}}"
            assert mensaje1 == mensaje2

            await asyncio.sleep(0.1)

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == GET_CARTAS_FIG
            assert mensaje1 == mensaje2

            await asyncio.sleep(0.1)

            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            assert mensaje1 == GET_BOARD
            assert mensaje1 == mensaje2
