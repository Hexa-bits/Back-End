from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict


GET_LOBBIES = "Actualizar lista de partidas"
END_TURN = "Terminó turno"
LEAVE_LOBBY = "Se unió/abandonó jugador en lobby"
CANCEL_LOBBY = "La partida se canceló"
GET_WINNER = "Hay Ganador"
GET_BOARD = "Hay modificación de Tablero"
GET_CARTAS_MOV = "Actualizar cartas de movimientos"
GET_CARTAS_FIG = "Actualizar cartas de figuras"
START_PARTIDA = "La partida inició"
JOIN_GAME = "Se unió/abandonó jugador en lobby"
GET_INFO_PLAYERS = "Actualizar cartas de otros jugadores"

def logs_format(player_name: str, event: str) -> str:
    return str({"type": "log", "data": {"player_name": player_name, "event": event}})

LOG_LEAVE = "Abandonó la partida"
LOG_END_TURN = "Terminó el turno"
LOG_USE_MOV = "Hizo un movimiento"
LOG_DISCARD_FIG = "Descartó una carta de figura"
LOG_CANCEL_MOV = "Canceló movimiento"

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
    
    async def send_get_lobbies(self):
        await self.send_message_game_id(GET_LOBBIES, 0)
    
    async def send_end_turn(self, game_id: int):
        await self.send_message_game_id(END_TURN, game_id)
    
    async def send_leave_lobby(self, game_id: int):
        await self.send_message_game_id(LEAVE_LOBBY, game_id)
    
    async def send_cancel_lobby(self, game_id: int):
        await self.send_message_game_id(CANCEL_LOBBY, game_id)
    
    async def send_get_winner(self, game_id: int):
        await self.send_message_game_id(GET_WINNER, game_id)
    
    async def send_get_tablero(self, game_id: int):
        await self.send_message_game_id(GET_BOARD, game_id)
    
    async def send_get_cartas_mov(self, game_id: int):
        await self.send_message_game_id(GET_CARTAS_MOV, game_id)
    
    async def send_get_cartas_fig(self, game_id: int):
        await self.send_message_game_id(GET_CARTAS_FIG, game_id)
    
    async def send_start_game(self, game_id: int):
        await self.send_message_game_id(START_PARTIDA, game_id)

    async def send_join_game(self, game_id: int):
        await self.send_message_game_id(JOIN_GAME, game_id)
    
    async def send_get_info_players(self, game_id: int):
        await self.send_message_game_id(GET_INFO_PLAYERS, game_id)

    async def send_leave_log(self, game_id: int, player_name: str):
        await self.send_message_game_id(logs_format(player_name, LOG_LEAVE), game_id)
    
    async def send_mov_log(self, game_id: int, player_name: str):
        await self.send_message_game_id(logs_format(player_name, LOG_USE_MOV), game_id)

    async def send_fig_log(self, game_id: int, player_name: str):
        await self.send_message_game_id(logs_format(player_name, LOG_DISCARD_FIG), game_id)

    async def send_turn_log(self, game_id: int, player_name: str):
        await self.send_message_game_id(logs_format(player_name, LOG_END_TURN), game_id)

    async def send_cancel_mov_log(self, game_id: int, player_name: str):
        await self.send_message_game_id(logs_format(player_name, LOG_CANCEL_MOV), game_id)

ws_manager = WebSocketConnectionManager()