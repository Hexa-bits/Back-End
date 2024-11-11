from fastapi import Depends, status, HTTPException, APIRouter
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError
from src.db import get_db
from sqlalchemy.orm import Session

from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.utils import Partida_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.ws_manager import ws_manager

from src.repositories.board_repository import *
from src.repositories.game_repository import *
from src.repositories.player_repository import *
from src.repositories.cards_repository import *
from src.game_helpers import *

router = APIRouter()

@router.websocket("")
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


@router.get("/get-lobbies", status_code=status.HTTP_200_OK)
async def get_lobbies(username: str, db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de pedir las lobbies al servidor.

    Respuesta:
    - 200: OK
    - 500: Ocurre un error interno.
    """
    try:
        lobbies = list_lobbies(username, db)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los lobbies.")
    return lobbies


@router.get("/lobby", status_code=status.HTTP_200_OK)
async def get_lobby_info(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de pedir al servidor la información de una
    lobby (jugadores, partida, cantidad maxima, etc).

    Respuesta:
    - 200: OK.
    - 500: Ocurre un error interno.
    """
    try:
        lobby_info = get_lobby(game_id.game_id, db)    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la partida")
    
    return lobby_info


@router.post("/create-config", status_code=status.HTTP_201_CREATED)
async def create_partida(partida_config: Partida_config, db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de crear una partida mediante un cierta configuración

    Respuesta:
    - 201: OK la partida fue creada.
    - 500: Ocurre un erro interno.
    """
    try:
        id_game = add_partida(partida_config, db)
        #Uso el block manager
        block_manager.create_game(id_game) #COMO SOLUCIONARLO
        block_manager.add_player(id_game, partida_config.id_user)
        #Luego de crear la partida, le actualizo a los ws conectados la nueva lista de lobbies
        await ws_manager.send_get_lobbies()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    
    return JSONResponse(
        content={"id": id_game},
        status_code=status.HTTP_201_CREATED
    ) 