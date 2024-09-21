from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError

from src.consultas import jugador_anfitrion, add_partida
from src.models.jugadores import Jugador
from src.models.inputs_front import Partida_config
from src.db import Base, engine, Session

Base.metadata.create_all(engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola, FastAPI!"}


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Datos inválidos", "detalles": exc.errors()},
    )


@app.post("/home/create_config")
async def create_partida(partida_config: Partida_config):
    try:
        id_game = add_partida(partida_config)
        jugador_anfitrion(partida_config.id_user)

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Fallo en la base de datos")
    
    return JSONResponse(
        content={"id": id_game}
    ) 