import asyncio
import json
import pytest
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.models.events import Event
from src.db import Base
from src.main import app, ws_manager
from unittest.mock import MagicMock, patch



@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

event = Event()

mock_partida = MagicMock()
mock_partida.id = 1
mock_partida.partida_iniciada = False

mock_jugador = MagicMock()
mock_jugador.id = 1
mock_jugador.partida_id = mock_partida.id
mock_jugador.es_anfitrion = True


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
        
        with patch("src.main.get_current_turn_player"), \
             patch("src.main.game_manager.is_tablero_parcial", return_value=False), \
             patch('src.main.terminar_turno', return_value = {"id_player": 1 ,
                                                                "name_player": "testuser"}), \
            patch('src.main.repartir_cartas', return_value= None), \
            patch("src.main.game_manager.set_jugador_en_turno_id"):
            # Simular una petición HTTP para obtener el siguiente turno
            response = client.put("/game/end-turn", json={"game_id": 1})

            # Esperar a que los lobbies se envíen a los clientes WebSocket conectados
            mensaje1 = websocket1.receive_text()
            mensaje2 = websocket2.receive_text()

            # Verificar que los mensajes recibidos son iguales para ambos
            assert mensaje1 == "Terminó turno"
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
            
            with patch('src.main.get_Jugador', return_value = jugadores_mock[0]), \
                 patch('src.main.get_Partida', return_value = partida_mock.return_value), \
                 patch('src.main.get_jugadores', side_effect=[jugadores_mock, [jugadores_mock.pop(0)]]), \
                 patch('src.main.delete_player', return_value = None):
                            
                response = client.put("/game/leave", json={"id_user": 1, "game_id": 1})
                assert response.status_code == 204

        # se cierra la conexion websocket1 simulando que el jugador abandono
        await asyncio.sleep(0.1)
        assert websocket2.receive_text() == "Actualizar cartas de otros jugadores"
        await asyncio.sleep(0.1)
        assert websocket2.receive_text() == "Hay Ganador"
        assert len(ws_manager.active_connections.get(1)) == 1
        #Borre la verificación posterior porque ya se hace en test_main

    await asyncio.sleep(0.1)
    
    assert len(ws_manager.active_connections) == 0


@pytest.mark.asyncio
async def test_websocket_broadcast_games_join(client):
    with client.websocket_connect("/game?game_id=1") as websocket1, \
         client.websocket_connect("/game?game_id=1") as websocket2:

        with patch("src.main.add_player_game", return_value=mock_jugador) as mock_add_partida, \
             patch("src.main.get_Partida", return_value=mock_partida) as mock_get_partida:
            config = {"player_id": 1 , "game_id": 1}
            mock_add_partida.return_value = mock_jugador

            response = client.post("/game/join", json=config)

            assert response.status_code == 200

            lobbies1 = websocket1.receive_text()
            lobbies2 = websocket2.receive_text()

            assert lobbies1 == event.join_game
            assert lobbies1 == lobbies2


@pytest.mark.asyncio
async def test_websocket_broadcast_games_leave(client):
    with client.websocket_connect("/game?game_id=1") as websocket1, \
         client.websocket_connect("/game?game_id=1") as websocket2:

        with patch("src.main.get_Jugador", return_value=mock_jugador) as mock_get_jugador, \
             patch("src.main.get_Partida", return_value=mock_partida) as mock_get_partida, \
             patch("src.main.delete_players_lobby") as mock_delete_players_partida:
            
            info_leave = {"id_user": 1, "game_id": 1}

            mock_get_jugador.return_value = mock_jugador
            mock_get_partida.return_value = mock_partida

            response = client.put("/game/leave", json=info_leave)

            assert response.status_code == 204

            lobbies1 = websocket1.receive_text()
            lobbies2 = websocket2.receive_text()

            assert lobbies1 == event.cancel_lobby
            assert lobbies1 == lobbies2
                            

@pytest.mark.asyncio
async def test_broadcast_message_to_other_websockets():
    with TestClient(app) as client:
        # Conecto 3 WebSockets
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

            # Recibo el mensaje en cada WebSocket
            received_1 = websocket_1.receive_text()
            received_2 = websocket_2.receive_text()
            received_3 = websocket_3.receive_text()

            # Verifico que los mensajes recibidos son iguales al enviado
            assert received_1 == response_text
            assert received_2 == response_text
            assert received_3 == response_text
