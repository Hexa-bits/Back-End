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

def get_fichas(game_id: int, db: Session):

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
    response = { "fichas": lista_fichas }
    
    return response

def mezclar_fichas(db: Session, game_id: int):

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