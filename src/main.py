from fastapi import FastAPI, Depends, status, HTTPException
from pydantic import BaseModel
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.cartafigura import pictureCard
from src.models.tablero import Tablero
from src.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session

from src.logic.lobby import list_lobbies
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permitir solicitudes desde tu front-end
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola, FastAPI!"}

@app.get("/home/get-lobbies")
async def get_lobbies(db: Session = Depends(get_db)):
    try:
        print("Obteniendo lobbies...")
        lobbies = list_lobbies(db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener los lobbies.")
    return lobbies