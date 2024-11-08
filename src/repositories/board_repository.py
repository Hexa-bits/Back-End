import random
import numpy as np
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from src.models.partida import Partida
from src.models.utils import *
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.game_helpers import detect_patterns, valid_figure, separate_arrays_by_color

def get_tablero(game_id: int, db: Session) -> Tablero:
    """
    Devuelve el tablero ó None si algo sale mal
    """
    smt = select(Tablero).where(Tablero.partida_id == game_id)
    return db.execute(smt).scalar()


def get_box_card(game_id: int, db: Session) -> List[FichaCajon]:
    """
    Devuelve las fichsaCajon de un juego ó None si algo sale mal
    """
    tablero = get_tablero(game_id, db)
    if (tablero is not None):
        smt = select(FichaCajon).where(FichaCajon.tablero_id == tablero.id)
        return db.execute(smt).scalars().all()
    return None


def get_box_card_coords(game_id: int, coords: Coords, db: Session) -> FichaCajon:
    """
    Devuelve la fichaCajon por sus coordenadas ó None si algo sale mal
    """
    tablero = get_tablero(game_id, db)
    if (tablero is not None):
        smt = select(FichaCajon).where (
                                        (FichaCajon.tablero_id == tablero.id) &     
                                        (FichaCajon.y_pos == coords.y_pos) & 
                                        (FichaCajon.x_pos == coords.x_pos)
        )
        return db.execute(smt).scalar()
    return None

def swap_box_card(game_id: int, tuple_coords: tuple[Coords, Coords], db: Session) -> None:
    """
    Swappea dos fichasCajon de acuerdo a sus coordenadas y juego.
    """
    box_card1 = get_box_card_coords(game_id, tuple_coords[0], db)
    box_card2 = get_box_card_coords(game_id, tuple_coords[1], db)

    if box_card1 is None or box_card2 is None:
        raise ValueError("Una o ambas fichasCajon no existe en la db")

    color_box_card_1= box_card1.color
    color_box_card_2= box_card2.color

    box_card1.color = color_box_card_2
    box_card2.color = color_box_card_1
    
    db.commit()


def get_tablero(game_id: int, db: Session) -> Tablero:
    """Función que retorna el tablero de una partida"""
    smt = select(Tablero).where(Tablero.partida_id == game_id)
    return db.execute(smt).scalar()


def get_box_card(tablero_id: int, db: Session) -> List[FichaCajon]:
    """Función que retorna las fichas de un tablero"""
    smt = select(FichaCajon).where(FichaCajon.tablero_id == tablero_id)
    return db.execute(smt).scalars().all()


def get_box_cards(game_id: int, db: Session) -> List[dict]:
    """Función que retorna las fichas de un tablero en formato lista de diccionarios"""
    tablero = db.query(Tablero).filter(Tablero.partida_id == game_id).first()

    all_box_cards = db.query(FichaCajon).filter(FichaCajon.tablero_id == tablero.id).all()

    list_box_cards = []
    for box_card in all_box_cards:
        #armo un json con las fichas
        list_box_cards.append({
            "x": box_card.x_pos,
            "y": box_card.y_pos,
            "color": box_card.color
        })
    
    return list_box_cards

def mezclar_box_cards(db: Session, game_id: int) -> int:
    """Función que mezcla las fichas del tablero"""

    tablero = Tablero(partida_id=game_id, color_prohibido=None)
    db.add(tablero)
    db.commit()
    db.refresh(tablero)

    #Creo una lista con las 36 coord
    coordenadas = []
    for i in range(1,7):
        for j in range(1,7):
            coordenadas.append((i,j))

    #Creo una lista con 9 veces repetido cada color del enum
    colors = [Color.ROJO]*9 + [Color.VERDE]*9 + [Color.AMARILLO]*9 + [Color.AZUL]*9

    #mezclo los colores que le corresponderia a cada casilla
    random.shuffle(colors)

    #Asigno cada color a una ficha cajon
    for coord in coordenadas:
        x, y = coord
        color = colors.pop()
        box_card = FichaCajon(x_pos=x, y_pos=y, color=color, tablero_id=tablero.id)
        db.add(box_card)
        db.commit()
        db.refresh(box_card)
        
    return tablero.id

def get_valid_detected_figures(game_id: int, list_patterns, db: Session ) -> List[List[Tuple[int, int]]]:
    """Función que retorna las figuras detectadas en el tablero que son válidas según los patrones dados y game_id"""
    list_box_cards = get_box_cards(game_id, db)

    matriz = np.zeros((6,6))
    for box_card in list_box_cards:
        x = box_card["x"]
        y = box_card["y"]
        matriz[x-1][y-1] = box_card["color"].value

    list_colors = [Color.ROJO.value, Color.VERDE.value, Color.AMARILLO.value, Color.AZUL.value]

    list_matrices_por_color = separate_arrays_by_color(matriz, list_colors)

    figuras_detectadas = []

    for matriz_color in list_matrices_por_color:
        figuras_detectadas.extend(detect_patterns(matriz_color, list_patterns))

    figuras_validas = []

    for figura in figuras_detectadas:
        if valid_figure(matriz, figura):
            figuras_validas.append(figura)

    return figuras_validas

def get_color_of_box_card( x_pos: int, y_pos: int, game_id: int, db: Session) -> Color:
    """Función que retorna el color de una ficha dada su x_pos, y_pos y game_id"""
    color = None

    tablero = get_tablero(game_id, db)

    if tablero:
        box_card = db.query(FichaCajon).filter(and_(FichaCajon.tablero_id == tablero.id, FichaCajon.x_pos == x_pos, FichaCajon.y_pos == y_pos)).first()

        if box_card:
            color = box_card.color

    return color
    
    