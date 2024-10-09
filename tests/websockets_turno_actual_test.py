import asyncio
import pytest
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.main import app, ws_manager
from unittest.mock import MagicMock, patch


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

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
    
    with client.websocket_connect("/game?game_id=1"):
        with client.websocket_connect("/game?game_id=1"):
            with client.websocket_connect("/game?game_id=2"):
                
                assert len(ws_manager.active_connections) == initial_connections + 2  
                assert len(ws_manager.active_connections.get(1)) == 2
                assert len(ws_manager.active_connections.get(2)) == 1    
    
    await asyncio.sleep(0.1)
    
    assert len(ws_manager.active_connections) == initial_connections


@pytest.mark.asyncio
async def test_websocket_broadcast_turno_siguiente(client):
    # Simular que un cliente se conecta al WebSocket
    with client.websocket_connect("/game?game_id=1") as websocket1:
        with client.websocket_connect("/game?game_id=1") as websocket2:
            assert len(ws_manager.active_connections) == 1  
            assert len(ws_manager.active_connections.get(1)) == 2 
            
            with patch('src.main.terminar_turno', return_value = {"id_player": 1 ,
                                                                  "name_player": "testuser"}):
                # Simular una petición HTTP para obtener el siguiente turno
                response = client.put("/game/end-turn", json={"game_id": 1})

                # Esperar a que los lobbies se envíen a los clientes WebSocket conectados
                mensaje1 = websocket1.receive_text()
                mensaje2 = websocket2.receive_text()

                # Verificar que los mensajes recibidos son iguales para ambos
                assert mensaje1 == "Terminó turno"
                assert mensaje1 == mensaje2
                assert response.status_code == 200
                assert response.json() == {"id_player": 1 , "name_player": "testuser"}
