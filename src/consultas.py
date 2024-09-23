from sqlalchemy.orm import Session
from src.models.partida import Partida
from src.models.inputs_front import Partida_config
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from sqlalchemy import select, func

def add_player(nombre: str, anfitrion: bool, db: Session) -> Jugador:
    jugador = Jugador(nombre= nombre, es_anfitrion= anfitrion)
    db.add(jugador)
    db.commit()  
    db.refresh(jugador)
    return jugador


def get_Jugador(id: int, db: Session) -> Jugador:
    smt = select(Jugador).where(Jugador.id == id)
    jugador = db.execute(smt).scalar()
    return jugador

def get_Partida(id: int, db: Session) -> Partida:
    smt = select(Partida).where(Partida.id == id)
    partida = db.execute(smt).scalar()
    return partida


def jugador_anfitrion(id: int, db: Session):
    jugador = get_Jugador(id, db)
    jugador.es_anfitrion = True
    db.commit()


def add_partida(config: Partida_config, db: Session) -> int:
    partida = Partida(game_name=config.game_name, max_players=config.max_players)
    db.add(partida)
    db.commit()
    db.refresh(partida)
    return partida.id


def delete_player(jugador: Jugador, db: Session):
    partida = get_Partida(jugador.partida_id, db)
    cant = player_in_partida(partida, db)
    if (partida.partida_iniciada and cant <= 2):
        delete_players_partida(partida, db)
    else: 
        jugador.partida_id = None
        db.commit()


def delete_partida(partida: Partida, db: Session):
    db.delete(partida)
    db.commit()


def delete_players_partida(partida: Partida, db: Session):
    smt = select(Jugador).where(Jugador.partida_id == partida.id)
    jugadores = db.execute(smt).scalars().all()
    for jugador in jugadores:
        jugador.partida_id = None
    db.commit()
    delete_partida(partida, db)


def player_in_partida(partida: Partida, db: Session) -> int:
    smt = select(func.count()).select_from(Jugador).where(Jugador.partida_id == partida.id)
    return db.execute(smt).scalar()