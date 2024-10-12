import random
from fastapi import FastAPI, Request, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
from pydantic import ValidationError, BaseModel

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.db import Base, engine, SessionLocal

from src.models.events import Event
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.utils import *
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon

from src.repositories.board_repository import *
from src.repositories.game_repository import *
from src.repositories.player_repository import *
from src.repositories.cards_repository import *
from src.game import GameManager
Base.metadata.create_all(bind=engine)

app = FastAPI()

game_manager = GameManager()
event = Event()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permitir solicitudes desde tu front-end
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

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

# Instanciar el WebSocketManager
ws_manager = WebSocketConnectionManager()

@app.websocket("/home")
async def websocket_endpoint(websocket: WebSocket):
    """
    Le permite al front escucha los mensajes entrantes, que se envían a
    todos aquellos en home
    """
    await ws_manager.connect(game_id=0, websocket=websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        await ws_manager.send_all_message("Un usuario se ha desconectado")


@app.websocket("/game")
async def websocket_endpoint(game_id: int, websocket: WebSocket):
    """
    Le permite al front escucha los mensajes entrantes, que se envían a
    todos aquellos en juego, ya sea lobby o en partida inciada por game_id
    """
    await ws_manager.connect(game_id=game_id, websocket=websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        await ws_manager.send_all_message("Un usuario se ha desconectado")

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola, FastAPI!"}


@app.get("/home/get-lobbies")
async def get_lobbies(db: Session = Depends(get_db)):
    try:
        lobbies = list_lobbies(db)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los lobbies.")
    return lobbies


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    En casos de error en la validación de tipos de los modelos Pydantic, el handler 
    captura la excepción y probee un error HTTP personalizado, especificando a detalle
    el error.  
    """
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())


@app.post("/login", response_model=PlayerId, status_code=status.HTTP_201_CREATED)
async def login(user: User, db: Session = Depends(get_db)):
    try:
        jugador = add_player(user.username, False, db)#Jugador(nombre= user.username, es_anfitrion=False)
    except Exception:
        db.rollback()  # Revertir cambios en caso de error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el usuario.")
    return PlayerId(player_id=jugador.id)


@app.get("/home/lobby")
async def get_lobby_info(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    try:
        lobby_info = get_lobby(game_id.game_id, db)    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la partida")
    
    return lobby_info


@app.post("/home/create-config", status_code=status.HTTP_201_CREATED)
async def create_partida(partida_config: Partida_config, db: Session = Depends(get_db)):
    try:
        id_game = add_partida(partida_config, db)

        #Luego de crear la partida, le actualizo a los ws conectados la nueva lista de lobbies
        await ws_manager.send_message_game_id(str(event.get_lobbies), game_id = 0)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    
    return JSONResponse(
        content={"id": id_game},
        status_code=status.HTTP_201_CREATED
    ) 


@app.put("/game/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_lobby(leave_lobby: Leave_config, db: Session=Depends(get_db)):
    try:
        jugador = get_Jugador(leave_lobby.id_user, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No existe el jugador: {leave_lobby.id_user}')
        
        partida = get_Partida(leave_lobby.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No exsite la partida: {leave_lobby.game_id}')
        
        if jugador.partida_id == None or jugador.partida_id != partida.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No exsite la partida asociada a jugador: {leave_lobby.id_user}')

        game_id = partida.id
        if partida.partida_iniciada:
            delete_player(jugador, db)
            if len(get_jugadores(partida.id, db)) == 1:
                #Mando ws
                await ws_manager.send_message_game_id(event.get_winner, partida.id)
        else:
            #Luego de abandonar la partida, le actualizo a los ws conectados la nueva lista de lobbies porque ahora tienen 1 jugador menos
            if jugador.es_anfitrion:
                delete_players_partida(partida, db)

                await ws_manager.send_message_game_id(event.cancel_lobby, game_id=game_id)
            else:
                delete_player(jugador, db)
                await ws_manager.send_message_game_id(event.leave_lobby, game_id=game_id)
        
            await ws_manager.send_message_game_id(str(event.get_lobbies), game_id = 0)

    
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    
    
@app.post("/game/join", response_model=PlayerAndGameId, status_code=status.HTTP_200_OK)
async def join_game(playerAndGameId: PlayerAndGameId, db: Session = Depends(get_db)):
    try:
        partida = get_Partida(playerAndGameId.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La partida no existe")
        
        jugador = add_player_game(playerAndGameId.player_id, playerAndGameId.game_id, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El jugador no existe")
        
        #Luego de unirse a la partida, le actualizo a los ws conectados la nueva lista de lobbies
        #Porque ahora tiene un jugador mas
        await ws_manager.send_message_game_id(str(event.get_lobbies), game_id = 0)
        await ws_manager.send_message_game_id(event.join_game, game_id=partida.id)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al unirse a partida")
    return PlayerAndGameId(player_id=jugador.id, game_id=jugador.partida_id)


@app.get("/game/board", status_code=status.HTTP_200_OK)
async def get_board(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    try:
        tablero = get_fichas(game_id.game_id, db)
        is_parcial = game_manager.is_tablero_parcial(game_id.game_id)

        response = { "fichas": tablero,
                    "parcial": is_parcial }

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el tablero")
    return response


@app.put("/game/end-turn", status_code=status.HTTP_200_OK)
async def end_turn(game_id: GameId, db: Session = Depends(get_db)):
    try:
        next_jugador = terminar_turno(game_id.game_id, db)
        game_manager.set_jugador_en_turno_id(game_id=game_id.game_id, jugador_id=next_jugador["id_player"])
       
        await ws_manager.send_message_game_id(event.end_turn, game_id.game_id)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al finalizar el turno")
    return next_jugador


@app.get("/game/my-fig-card/", status_code=status.HTTP_200_OK)
async def get_mov_card(player_id: PlayerId = Depends(), db: Session = Depends(get_db)):
    try:
        id_fig_cards = list_fig_cards(player_id.player_id, db)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse (    
        content={"id_fig_card": id_fig_cards},
        status_code=status.HTTP_200_OK
    )


@app.get("/game/my-mov-card", status_code=status.HTTP_200_OK)
async def get_mov_card(player_id: PlayerId = Depends(), db: Session = Depends(get_db)):
    try:
        id_mov_cards = list_mov_cards(player_id.player_id, db)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content={"id_mov_card": id_mov_cards},
        status_code=status.HTTP_200_OK
    )


@app.get("/game/get-winner", status_code=status.HTTP_200_OK)
async def get_winner(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    try:
        winner = get_jugadores(game_id.game_id, db)[0]
  
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content= {"name_player": winner.nombre}
    )
    

@app.get("/game/current-turn", status_code=status.HTTP_200_OK)
async def get_current_turn(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    try:
        jugador = jugador_en_turno(game_id.game_id, db)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el jugador actual en turno")
    return jugador


@app.put("/game/start-game", status_code= status.HTTP_200_OK)
async def start_game(game_id: GameId, db: Session = Depends(get_db)):
    try:
        partida = get_Partida(game_id.game_id, db)
        if not partida.partida_iniciada:
            mezclar_fichas(db, game_id.game_id)
            mezclar_cartas_movimiento(db, game_id.game_id)
            mezclar_figuras(game_id.game_id, db)
            asignar_turnos(game_id.game_id, db)
            partida.partida_iniciada = True
            db.commit()
            #Envio la lista de partidas actualizadas a ws ya que se inicio una partida
            await ws_manager.send_message_game_id(str(event.get_lobbies), game_id = 0)
            await ws_manager.send_message_game_id(event.start_partida, game_id.game_id)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content={"id_game": game_id.game_id, "iniciada": partida.partida_iniciada},
        status_code=status.HTTP_200_OK
    )


@app.post("/game/cancel-mov", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_mov(playerAndGameId: PlayerAndGameId, db: Session = Depends(get_db)):
    """
    Reestablece las últimas fichas cajon intercambiadas y devuelve la carta de 
    movimiento descartada a la mano del jugador en turno.
    """
    try:
        jugador = get_Jugador(playerAndGameId.player_id, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f'No existe el jugador: {playerAndGameId.player_id}')
        
        partida = get_Partida(playerAndGameId.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f'No exsite la partida: {playerAndGameId.game_id}')
        
        if jugador.partida_id == None or jugador.partida_id != partida.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No exsite la partida asociada a jugador: {playerAndGameId.player_id}')
        
        if jugador.id != partida.jugador_en_turno:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No es el turno del jugador: {jugador.id}, es de: {partida.jugador_en_turno}')

        mov_coords = game_manager.top_tupla_carta_y_fichas(game_id=jugador.id)
        if mov_coords is not None:
            cancelar_movimiento(partida=partida, jugador=jugador, mov=mov_coords[0],
                                 coords=(Coords(**mov_coords[1][0]), Coords(**mov_coords[1][1])), db=db)

            await ws_manager.send_message_game_id(event.get_tablero, jugador.id)
            await ws_manager.send_message_game_id(event.get_movimientos, jugador.id)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No hay movimientos que deshacer')

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    
    mov_coords = game_manager.desapilar_carta_y_ficha(game_id=jugador.id) #popeo cuando me aseguro que el se ha efectuado el efecto en la db