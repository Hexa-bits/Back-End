from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from sqlalchemy.orm import Session

def add_player(nombre: str, anfitrion: bool, db: Session):
    jugador = Jugador(nombre= nombre, es_anfitrion= anfitrion)
    db.add(jugador)
    db.commit()  
    db.refresh(jugador)
    return jugador