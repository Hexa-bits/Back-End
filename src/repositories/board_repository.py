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
from src.models.inputs_front import Coords

def get_tablero(game_id: int, db: Session) -> Tablero:
    smt = select(Tablero).where(Tablero.partida_id == game_id)
    return db.execute(smt).scalar()


def get_fichasCajon(game_id: int, db: Session) -> List[FichaCajon]:
    tablero = get_tablero(game_id, db)
    smt = select(FichaCajon).where(FichaCajon.tablero_id == tablero.id)
    return db.execute(smt).scalars().all()


def get_fichaCajon_coords(game_id: int, coords: Coords, db: Session) -> FichaCajon:
    tablero = get_tablero(game_id, db)
    smt = select(FichaCajon).where (
                                    (FichaCajon.tablero_id == tablero.id) &     
                                    (FichaCajon.y_pos == coords.y) & 
                                    (FichaCajon.x_pos == coords.x)
    )
    return db.execute(smt).scalar()


def swap_fichasCajon(game_id: int, tupla_coords: tuple[Coords, Coords], db: Session) -> None:
    ficha1 = get_fichaCajon_coords(game_id, tupla_coords[0], db)
    ficha2 = get_fichaCajon_coords(game_id, tupla_coords[1], db)
    ficha1, ficha2 = ficha2, ficha1    


def get_fichas(game_id: int, db: Session) -> List[dict]:

    tablero = db.query(Tablero).filter(Tablero.partida_id == game_id).first()

    all_fichas = db.query(FichaCajon).filter(FichaCajon.tablero_id == tablero.id).all()

    lista_fichas = []
    for ficha in all_fichas:
        #armo un json con las fichas
        lista_fichas.append({
            "x": ficha.x_pos,
            "y": ficha.y_pos,
            "color": ficha.color
        })
    
    return lista_fichas

def mezclar_fichas(db: Session, game_id: int) -> int:

    tablero = Tablero(partida_id=game_id)
    db.add(tablero)
    db.commit()
    db.refresh(tablero)

    #Creo una lista con las 36 coord
    coordenadas = []
    for i in range(1,7):
        for j in range(1,7):
            coordenadas.append((i,j))

    #Creo una lista con 9 veces repetido cada color del enum
    colores = [Color.ROJO]*9 + [Color.VERDE]*9 + [Color.AMARILLO]*9 + [Color.AZUL]*9

    #mezclo los colores que le corresponderia a cada casilla
    random.shuffle(colores)

    #Asigno cada color a una ficha cajon
    for coord in coordenadas:
        x, y = coord
        color = colores.pop()
        ficha = FichaCajon(x_pos=x, y_pos=y, color=color, tablero_id=tablero.id)
        db.add(ficha)
        db.commit()
        db.refresh(ficha)
        
    return tablero.id