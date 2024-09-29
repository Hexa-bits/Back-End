from fastapi import FastAPI, Request, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel

from sqlalchemy.exc import SQLAlchemyError
from src.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session

from src.models.jugadores import Jugador
from src.models.inputs_front import Partida_config
from src.models.partida import Partida
from src.models.tablero import Tablero

from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon

from sqlalchemy.orm import Session
from src.consultas import add_player
from src.consultas import add_player, add_partida, list_lobbies, asignar_turnos

from sqlalchemy.exc import IntegrityError


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

