import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from src.models.partida import Partida
from src.models.utils import Partida_config
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

def get_players(game_id: int, db: Session) -> List[Jugador]:
    return db.query(Jugador).filter(Jugador.partida_id == game_id).all()

def get_jugador_sin_cartas(game_id: int, db: Session) -> Jugador:
    return db.query(Jugador).outerjoin(PictureCard).filter (
                                                            Jugador.partida_id == game_id,
                                                            PictureCard.id == None
                                                            ).one_or_none()

def get_current_turn_player(game_id: int, db: Session) -> Jugador:
    partida = get_Partida(game_id, db)
    if partida is not None:
        smt = select(Jugador).where(and_(
                                        Jugador.partida_id == game_id, 
                                        Jugador.turno == partida.jugador_en_turno
                                        )
                                    )
        return db.execute(smt).scalar()
    return None

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

def asignar_turnos(game_id: int, db: Session) -> None:
    player_list = get_players(game_id, db)           #db.query(Jugador).filter(Jugador.partida_id == game_id).all()

    turnos = random.sample(range(len(player_list)), len(player_list))

    for jugador, turno in zip(player_list, turnos):
        jugador.turno = turno
        db.commit()
        db.refresh(jugador)

def delete_players_lobby(partida: Partida, db: Session) -> None:
    smt = select(Jugador).where(Jugador.partida_id == partida.id)
    jugadores = db.execute(smt).scalars().all()
    for jugador in jugadores:
        if (jugador.es_anfitrion):
            jugador.es_anfitrion = False
            
        jugador.partida_id = None
    db.commit()
    delete_partida(partida, db)


def num_players_in_game(partida: Partida, db: Session) -> int:
    smt = select(func.count()).select_from(Jugador).where(Jugador.partida_id == partida.id)
    return db.execute(smt).scalar()

def delete_player(jugador: Jugador, db: Session) -> bool:
    partida = get_Partida(jugador.partida_id, db)
    if partida:
        cant = num_players_in_game(partida, db)
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

def add_partida(config: Partida_config, db: Session) -> int:
    partida = Partida(game_name=config.game_name, 
                      max_players=config.max_players,
                      password=config.game_password if config.game_password != ""
                      else None)
    
    jugador = get_Jugador(config.id_user, db)
    db.add(partida)
    db.commit()
    db.refresh(partida)
    jugador.es_anfitrion = True
    jugador.partida_id = partida.id
    db.commit()
    return partida.id