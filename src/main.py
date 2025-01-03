from fastapi import FastAPI, Request, Depends, status, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from sqlalchemy.orm import Session

from src.db import Base, engine, get_db

from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.utils import *
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.models.fichas_cajon import FichaCajon

from src.repositories.board_repository import *
from src.repositories.game_repository import *
from src.repositories.player_repository import *
from src.repositories.cards_repository import *
from src.routers import game, home

Base.metadata.create_all(bind=engine)
app = FastAPI(
        openapi_tags=[
        {
            "name": "base",
            "description": "Operaciones inciales o auxiliares para el sistema.",
        },
        {
            "name": "home",
            "description": "Operaciones relacionadas con la gestión de lobbies.",
        },
        {
            "name": "game",
            "description": "Gestión de partidas, desde la creación hasta la finalización.",
        },
    ]
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permitir solicitudes desde tu front-end
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

app.include_router(home.router, prefix="/home", tags=["home"])
app.include_router(game.router, prefix="/game", tags=["game"])

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    En casos de error en la validación de tipos de los modelos Pydantic, el handler 
    captura la excepción y probee un error HTTP personalizado, especificando a detalle
    el error.  
    """
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())

@app.get("/", tags=["base"])
def read_root():
    """
    Verifica que el back este andando
    """
    return {"mensaje": "¡Hola, FastAPI!"}


@app.post("/login", tags=["base"], response_model=PlayerId, status_code=status.HTTP_201_CREATED)
async def login(user: User, db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de logearse como usuario. Crea una instancia
    de jugador, en funcion de parametros válidos.

    Respuesta:
    - 200: OK
    - 500: Ocurre un error interno.
    """
    try:
        player = add_player(user.username, False, db)
    except Exception:
        db.rollback()  # Revertir cambios en caso de error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el usuario.")
    return JSONResponse(
        content={"id": player.id},
        status_code=status.HTTP_201_CREATED
    )
