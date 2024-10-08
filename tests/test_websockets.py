import asyncio
import pytest
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.main import app, ws_manager
from src.models.events import Event

event = Event()

# Probar la conexión de WebSocket
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.mark.asyncio
async def test_websocket_connection(client):
    # Comprobar cuántas conexiones activas hay antes de la conexión
    initial_connections = len(ws_manager.active_connections)

    #Simulo una conexión al WebSocket
    with client.websocket_connect("/home/") as websocket:
        # Verificar que el WebSocket se conectó correctamente
        assert websocket is not None

        # Verificar que la cantidad de conexiones activas aumentó
        assert len(ws_manager.active_connections) == initial_connections + 1        
    
    await asyncio.sleep(0.1)
    # Después de cerrar la conexión, verificar que la cantidad de conexiones activas disminuyó
    assert len(ws_manager.active_connections) == initial_connections


@pytest.mark.asyncio
async def test_websocket_broadcast_lobbies(client):
    # Simular que un cliente se conecta al WebSocket
    with client.websocket_connect("/home/") as websocket1:
        with client.websocket_connect("/home/") as websocket2:
            # Simular una petición HTTP para obtener lobbies
            response = client.get("/home/get-lobbies")
            assert response.status_code == 200

            #Esto se modificara en list_lobbies_ws nuevo (rama HB-88)

            #Esperar a que los lobbies se envíen a los clientes WebSocket conectados
            lobbies1 = websocket1.receive_text()
            lobbies2 = websocket2.receive_text()

            assert lobbies1 is not None
            assert lobbies2 is not None

            #Me aseguro que el ws recibe el mensaje de evento correcto
            assert lobbies1 == event.get_lobbies

            # Verificar que los mensajes recibidos son iguales para ambos
            assert lobbies1 == lobbies2

