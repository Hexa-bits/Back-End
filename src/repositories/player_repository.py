import random
import json
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from src.models.partida import Partida
from src.models.inputs_front import Partida_config
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov

from src.repositories.cards_repository import cards_to_mazo
from src.repositories.game_repository import delete_partida, get_Partida, terminar_turno




def get_Jugador(id: int, db: Session) -> Jugador:
    smt = select(Jugador).where(Jugador.id == id)
    jugador = db.execute(smt).scalar()
    return jugador

def get_jugadores(game_id: int, db: Session):
    return db.query(Jugador).filter(Jugador.partida_id == game_id).all()

def get_ordenes(id_game: int, db: Session) -> List[Jugador]:
    smt = select(Jugador).where(Jugador.partida_id == id_game)
    jugadores = db.execute(smt).scalars().all()
    jugadores.sort(key=lambda jugador: jugador.turno)
    return jugadores

def add_player(nombre: str, anfitrion: bool, db: Session) -> Jugador:
    jugador = Jugador(nombre= nombre, es_anfitrion= anfitrion)
    db.add(jugador)
    db.commit()  
    db.refresh(jugador)
    return jugador

def add_player_game(player_id: int, game_id: int, db: Session) -> Jugador:
    jugador = get_Jugador(player_id, db)
    jugador.partida_id = game_id
    db.commit()
    db.refresh(jugador)
    return jugador

def asignar_turnos(game_id: int, db: Session):
    player_list = get_jugadores(game_id, db)           #db.query(Jugador).filter(Jugador.partida_id == game_id).all()

    turnos = random.sample(range(len(player_list)), len(player_list))

    for jugador, turno in zip(player_list, turnos):
        jugador.turno = turno
        db.commit()
        db.refresh(jugador)

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

def delete_player(jugador: Jugador, db: Session):
    partida = get_Partida(jugador.partida_id, db)
    cant = player_in_partida(partida, db)
    if (partida.partida_iniciada):
        if (partida.jugador_en_turno == jugador.turno):
            terminar_turno(partida.id, db)

        cards_to_mazo(partida, jugador, db)

        if (jugador.es_anfitrion):
            jugador.es_anfitrion = False
        
        if (cant == 1):
            delete_partida(partida, db)
    
    jugador.partida_id = None
    db.commit()

