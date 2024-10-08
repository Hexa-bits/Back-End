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

from src.repositories.cards_repository import get_cartasMovimiento_game

def get_Partida(id: int, db: Session) -> Partida:
    smt = select(Partida).where(Partida.id == id)
    partida = db.execute(smt).scalar()
    return partida

def get_lobby(game_id: int, db: Session):
    try:
        partida = db.query(Partida).filter(Partida.id == game_id).first()
    except Exception:
        raise Exception("Error al obtener la partida")
    
    if partida is None:
        raise Exception("No existe la partida")
    
    lista_jugadores = []
    
    try:
    #List of players name order by es_anfitrion==True first
        jugadores_en_partida = db.query(Jugador).filter(Jugador.partida_id == game_id).order_by(Jugador.es_anfitrion.desc()).all()
        for jugador in jugadores_en_partida:
            lista_jugadores.append(jugador.nombre)
    except Exception:
        raise Exception("Error al obtener los jugadores de la partida")

    lobby_info = {
        "game_name": partida.game_name,
        "max_players": partida.max_players,
        "game_status": partida.partida_iniciada,
        "name_players": lista_jugadores
    }

    return lobby_info

def jugador_en_turno(game_id: int, db: Session):
        
    partida = db.query(Partida).filter(Partida.id == game_id).first()

    turno_actual = partida.jugador_en_turno

    #Obtengo el jugador en turno actual de partida_id == game_id
    jugador_turno_actual = db.query(Jugador).filter(Jugador.turno == turno_actual,
                                                    Jugador.partida_id == game_id).first()

    jugador_response = {
        "id_player": jugador_turno_actual.id,
        "name_player": jugador_turno_actual.nombre
    }
    
    return jugador_response

def terminar_turno(game_id: int, db: Session):
    #Obtengo la partida
    try:
        partida = db.query(Partida).filter(Partida.id == game_id).first()
        jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).order_by(Jugador.turno).all()

    except Exception:
        raise Exception("Error")
    
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
    
    json_jugador_turno = {
        "id_player": jugadores[new_index].id ,
        "name_player": jugadores[new_index].nombre
    }
    
    #Debo retornar lo que esta en la API formato JSON
    return json_jugador_turno

def list_lobbies(db):

    raw_lobbies = db.query(Partida).all()
    
    lobbies = []

    for lobby in raw_lobbies:
        #Calculo la cantidad de jugadores actuales en partida
        current_players = db.query(Jugador).filter(Jugador.partida_id == lobby.id).count()
        if current_players == 0 or lobby.partida_iniciada:
            continue
        lobbies.append({
            "game_id": lobby.id,
            "game_name": lobby.game_name,
            "current_players": current_players,
            "max_players": lobby.max_players,
            })

    return lobbies

def list_lobbies_ws(db):
    response_http = list_lobbies(db)
    response_ws = json.dumps(response_http)
    return response_ws

def delete_partida(partida: Partida, db: Session):
    if (partida.partida_iniciada):
        movs = get_cartasMovimiento_game(partida.id, db)
        for mov in movs:
            mov.partida_id = None
            db.delete(mov)
        #A FUTURO SERA NECESARIO ELIMINAR EL TABLERO Y LAS FICHAS ASOCIADAS A LA PARTIDA TAMBIEN

    db.delete(partida)
    db.commit()

