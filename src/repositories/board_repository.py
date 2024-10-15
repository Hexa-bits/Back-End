import random
import numpy as np
import json
from typing import List, Tuple
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

from src.game import detectar_patrones, figura_valida, separar_matrices_por_color

def get_tablero(game_id: int, db: Session) -> Tablero:
    """Función que retorna el tablero de una partida"""
    smt = select(Tablero).where(Tablero.partida_id == game_id)
    return db.execute(smt).scalar()


def get_fichasCajon(tablero_id: int, db: Session) -> List[FichaCajon]:
    """Función que retorna las fichas de un tablero"""
    smt = select(FichaCajon).where(FichaCajon.tablero_id == tablero_id)
    return db.execute(smt).scalars().all()


def get_fichas(game_id: int, db: Session) -> List[dict]:
    """Función que retorna las fichas de un tablero en formato lista de diccionarios"""
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
    """Función que mezcla las fichas del tablero"""

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

def get_valid_detected_figures(game_id: int, lista_patrones, db: Session ) -> List[List[Tuple[int, int]]]:
    """Función que retorna las figuras detectadas en el tablero que son válidas según los patrones dados y game_id"""
    lista_fichas = get_fichas(game_id, db)

    matriz = np.zeros((6,6))
    for ficha in lista_fichas:
        x = ficha["x"]
        y = ficha["y"]
        matriz[x-1][y-1] = ficha["color"].value

    lista_colores = [Color.ROJO.value, Color.VERDE.value, Color.AMARILLO.value, Color.AZUL.value]

    lista_matrices_por_color = separar_matrices_por_color(matriz, lista_colores)

    figuras_detectadas = []

    for matriz_color in lista_matrices_por_color:
        figuras_detectadas.extend(detectar_patrones(matriz_color, lista_patrones))

    figuras_validas = []

    for figura in figuras_detectadas:
        if figura_valida(matriz, figura):
            figuras_validas.append(figura)

    return figuras_validas

def get_color_of_ficha( x_pos: int, y_pos: int, game_id: int, db: Session) -> Color:
    """Función que retorna el color de una ficha dada su x_pos, y_pos y game_id"""
    color = None

    tablero = get_tablero(game_id, db)

    if tablero:
        ficha = db.query(FichaCajon).filter(and_(FichaCajon.tablero_id == tablero.id, FichaCajon.x_pos == x_pos, FichaCajon.y_pos == y_pos)).first()

    if ficha:
        color = ficha.color


    return color