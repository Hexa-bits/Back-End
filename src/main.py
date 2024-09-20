from fastapi import FastAPI, Depends, status, HTTPException
from pydantic import BaseModel
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.cartafigura import pictureCard
from src.models.tablero import Tablero
from src.db import Base, engine, SessionLocal
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close

class PlayerId(BaseModel):
    id: int

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola, FastAPI!"}

# Endpoint para jugador /login

@app.post("/login", response_model=PlayerId, status_code=status.HTTP_201_CREATED)
async def login(username: str, db: Session = Depends(get_db)):
    jugador = Jugador(nombre=username, es_anfitrion=False)
    db.add(jugador)
    try:
        db.commit()  
        db.refresh(jugador)
    except Exception as e:
        db.rollback()  # Revertir cambios en caso de error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el usuario.")
    return PlayerId(id=jugador.id)
