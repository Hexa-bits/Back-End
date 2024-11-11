from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from src.models.partida import Partida
from src.models.utils import Partida_config, Coords
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.repositories.cards_repository import get_cartasMovimiento_game
from src.repositories.board_repository import get_tablero, get_box_card

def get_Partida(id: int, db: Session) -> Partida:
    smt = select(Partida).where(Partida.id == id)
    partida = db.execute(smt).scalar()
    return partida

def get_lobby(game_id: int, db: Session) -> List[dict]:
    try:
        partida = db.get(Partida, game_id)
    except Exception:
        raise Exception("Error al obtener la partida")
    
    if partida is None:
        raise Exception("No existe la partida")
    
    list_jugadores = []
    
    try:
    #List of players name order by es_anfitrion==True first
        jugadores_en_partida = db.query(Jugador).filter(Jugador.partida_id == game_id).order_by(Jugador.es_anfitrion.desc()).all()
        for jugador in jugadores_en_partida:
            list_jugadores.append(jugador.nombre)
    except Exception:
        raise Exception("Error al obtener los jugadores de la partida")

    lobby_info = {
        "game_name": partida.game_name,
        "max_players": partida.max_players,
        "game_status": partida.partida_iniciada,
        "name_players": list_jugadores
    }

    return lobby_info

def jugador_en_turno(game_id: int, db: Session) -> dict:
        
    partida = db.get(Partida, game_id)

    turno_actual = partida.jugador_en_turno

    #Obtengo el jugador en turno actual de partida_id == game_id
    jugador_turno_actual = db.query(Jugador).filter(Jugador.turno == turno_actual,
                                                    Jugador.partida_id == game_id).first()

    jugador_response = {
        "id_player": jugador_turno_actual.id,
        "name_player": jugador_turno_actual.nombre
    }
    
    return jugador_response

def terminar_turno(game_id: int, db: Session) -> dict:
    #Obtengo la partida
    partida = db.get(Partida, game_id)

    if partida:
        jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).order_by(Jugador.turno).all()
        
        #hago una lista con los indices de los jugadores
        lista_turnos = [x.turno for x in jugadores]
    
        turno = partida.jugador_en_turno
    
        #Busco que lugar de la lista esta el jugador en turno
        index = lista_turnos.index(turno)
    
        #indice del proximo jugador
        new_index = index + 1
        #Si me paso del final de la lista tomo  el primer jugador de nuevo
        if new_index == len(jugadores):
            new_index = 0
            
        partida.jugador_en_turno = lista_turnos[new_index]
        db.commit()
        
        info_jugador_turno = {
            "id_player": jugadores[new_index].id ,
            "name_player": jugadores[new_index].nombre
        }
        
        #Debo retornar lo que esta en la API formato JSON
        return info_jugador_turno


def is_name_in_started_game(game_id: int, username: str, db: Session) -> bool:

    jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).all()
    for jugador in jugadores:
        if jugador.nombre == username:
            return True
    return False

def get_player_id_in_game_by_name(game_id: int, username: str, db: Session) -> int: 
    jugador = db.query(Jugador).filter(Jugador.partida_id == game_id, Jugador.nombre == username).first()
    return jugador.id

def list_lobbies(username: str,db: Session) -> List[dict]:

    raw_lobbies = db.query(Partida).all()
    
    lobbies = []

    for lobby in raw_lobbies:

        name_in_started_game = is_name_in_started_game(lobby.id, username, db)

        #Calculo la cantidad de jugadores actuales en partida
        current_players = db.query(Jugador).filter(Jugador.partida_id == lobby.id).count()
        if current_players == 0 or (lobby.partida_iniciada and not name_in_started_game):
            continue
        lobbies.append({
            "game_id": lobby.id,
            "game_name": lobby.game_name,
            "current_players": current_players,
            "max_players": lobby.max_players,
            "started": lobby.partida_iniciada,
            })

    return lobbies

def delete_partida(partida: Partida, db: Session) -> None:
    if (partida.partida_iniciada):
        movs = get_cartasMovimiento_game(partida.id, db)
        for mov in movs:
            mov.partida_id = None
            db.delete(mov)
        
        tablero = get_tablero(partida.id, db)
        box_cards = get_box_card(tablero.id, db)
        for box_card in box_cards:
            box_card.tablero_id = None
            db.delete(box_card)
        
        tablero.partida_id = None
        db.delete(tablero)

    db.delete(partida)
    db.commit()