from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict

class WebSocketConnectionManager:
    """
    Maneger de conexiones con ws, se utiliza para establecer conexiones entrantes,
    manejar las desconexiones y enviar mensajes a todos aquellos en una misma
    partida/home.
    """
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, game_id: int, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket):
        for game_id, connections in self.active_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.active_connections[game_id]
                break 

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_all_message(self, message: str):
        for game_id, connections in self.active_connections.items():
            for connection in connections:
                await connection.send_text(message)
    
    async def send_message_game_id(self, message: str, game_id: int):
        for id_game, connections in self.active_connections.items():
            if id_game == game_id:
                for connection in connections:
                    await connection.send_text(message)
                break