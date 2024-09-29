from fastapi import FastAPI, Request, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel

from sqlalchemy.exc import SQLAlchemyError
from src.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session

from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.inputs_front import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.consultas import *

from sqlalchemy.exc import IntegrityError

import random

Base.metadata.create_all(bind=engine)


app = FastAPI()

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


class PlayerId(BaseModel):
    id: int


class User(BaseModel):
    username: str

class GameId(BaseModel):
    game_id: int

class PlayerAndGameId(BaseModel):
    game_id: int
    player_id: int

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
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())


# Endpoint para jugador /login

@app.post("/login", response_model=PlayerId, status_code=status.HTTP_201_CREATED)
async def login(user: User, db: Session = Depends(get_db)):
    try:
        jugador = add_player(user.username, False, db)#Jugador(nombre= user.username, es_anfitrion=False)
    except Exception:
        db.rollback()  # Revertir cambios en caso de error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el usuario.")
    return PlayerId(id=jugador.id)

#Endpoint para get info lobby
@app.get("/home/lobby")
async def get_lobby_info(game_id: int, db: Session = Depends(get_db)):
    try:
        lobby_info = get_lobby(game_id, db)
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener la partida")
    
    return lobby_info


@app.post("/home/create-config", status_code=status.HTTP_201_CREATED)
async def create_partida(partida_config: Partida_config, db: Session = Depends(get_db)):
    try:
        id_game = add_partida(partida_config, db)
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
        if partida is None or partida.partida_iniciada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No exsite la partida: {leave_lobby.game_id}')
        
        if jugador.partida_id == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No exsite la partida asociada a jugador: {leave_lobby.id_user}')

        if jugador.es_anfitrion:
            delete_players_partida(partida, db)
        else:
            delete_player(jugador, db)
        
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
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al unirse a partida")
    return PlayerAndGameId(player_id=jugador.id, game_id=jugador.partida_id)

@app.put("/game/end-turn", status_code=status.HTTP_200_OK)
async def end_turn(game_id: GameId, db: Session = Depends(get_db)):
    try:
        next_jugador = terminar_turno(game_id.game_id, db)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al finalizar el turno")
    return next_jugador

def mezclar_figuras(game_id: int, db: Session = Depends(get_db)):
    figuras_list = [x for x in range(1, 26)] + [x for x in range(1, 26)]
    random.shuffle(figuras_list)
    repartir_cartas_figuras(game_id, figuras_list, db)
    
