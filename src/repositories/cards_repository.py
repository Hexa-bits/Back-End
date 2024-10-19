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

def get_CartaFigura(id_carta_figura: int, db: Session) -> PictureCard:
    smt = select(PictureCard).where(PictureCard.id == id_carta_figura)
    return db.execute(smt).scalar() 

def get_CartaMovimiento(id_carta_movimiento: int, db: Session) -> MovementCard:
    smt = select(MovementCard).where(MovementCard.id == id_carta_movimiento)
    return db.execute(smt).scalar() 

def list_fig_cards(player_id: int, db: Session) -> List[int]:
    smt = select(PictureCard.figura).where(and_(PictureCard.jugador_id == player_id, PictureCard.estado == CardState.mano))
    cards = db.execute(smt).scalars().all()
    res = []
    for card in cards:
        res.append(card.value)
    return res 

def list_mov_cards(player_id: int, db: Session) -> List[MovementCard]:
    smt = select(MovementCard).where(and_(MovementCard.jugador_id == player_id, MovementCard.estado == CardStateMov.mano))
    return db.execute(smt).scalars().all()

def mezclar_figuras(game_id: int, db: Session) -> None:
    figuras_list = [x for x in range(1, 26)] + [x for x in range(1, 26)]
    random.shuffle(figuras_list)
    repartir_cartas_figuras(game_id, figuras_list, db)

def mezclar_cartas_movimiento(db: Session, game_id: int) -> None:
    #Creo las cartas de movimiento
    cards_mov_type = [Move.linea_contiguo,Move.linea_con_espacio,
                    Move.diagonal_contiguo,Move.diagonal_con_espacio,
                    Move.L_derecha,Move.L_izquierda,Move.linea_al_lateral]
    
    for card_type in cards_mov_type:
        for i in range (7):
            #Añado la carta en la db
            carta_mov = MovementCard(movimiento=card_type, partida_id=game_id )
            db.add(carta_mov)
            db.commit()
            db.refresh(carta_mov)
    
    all_cards_mov = db.query(MovementCard).filter(MovementCard.partida_id == game_id).all()
    
    #Mezclo las cartas
    random.shuffle(all_cards_mov)
        
    #Obtengo 3 cartas para cada jugador
    #Obtengo mi lista de jugadores
    jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).all()
    
    for jugador in jugadores:
        for i in range(3):
            #Obtengo una carta aleatoria de all_cards_mov
            carta = all_cards_mov.pop()
            carta.jugador_id = jugador.id
            carta.estado = CardStateMov.mano
            db.commit()
            db.refresh(carta)
    return

def repartir_cartas_figuras (game_id: int, figuras_list: List[int], db: Session) -> None:
    jugadores = get_ordenes(game_id, db)
    num_jugadores = len(jugadores)

    cartas_total = (50 // num_jugadores) *num_jugadores

    for i in range(cartas_total):

        cartaFigura = PictureCard(figura=Picture(figuras_list[i]))
        if (i < 3 *num_jugadores):
            cartaFigura.estado = CardState.mano

        cartaFigura.partida_id = game_id
        cartaFigura.jugador_id = jugadores[i % num_jugadores].id
        i += num_jugadores
        db.add(cartaFigura)

    db.commit()

def cards_to_mazo(partida: Partida, jugador: Jugador, db: Session) -> None:
    figs = get_cartasFigura_player(jugador.id, db)
    for fig in figs:
        fig.partida_id = None
        fig.jugador_id = None
        db.delete(fig)
    
    movs = get_cartasMovimiento_player(partida.id, db)
    for mov in movs:
        mov.jugador_id = None
        mov.estado = CardStateMov.mazo
    
    db.commit()

def get_cartasFigura_player(player_id: int, db: Session) -> List[PictureCard]:
    smt = select(PictureCard).where(PictureCard.jugador_id == player_id)
    return db.execute(smt).scalars().all()


def get_cartasMovimiento_player(player_id: int, db: Session) -> List[MovementCard]:
    smt = select(MovementCard).where(MovementCard.jugador_id == player_id)
    return db.execute(smt).scalars().all()


def get_cartasMovimiento_game(game_id: int, db: Session) -> List[MovementCard]:
    smt = select(MovementCard).where(MovementCard.partida_id == game_id)
    return db.execute(smt).scalars().all()

def get_ordenes(id_game: int, db: Session) -> List[Jugador]:
    smt = select(Jugador).where(Jugador.partida_id == id_game)
    jugadores = db.execute(smt).scalars().all()
    jugadores.sort(key=lambda jugador: jugador.turno)
    return jugadores

def others_cards(game_id: int, player_id: int, db: Session) -> List[dict]:

    #obtengo los jugadores de la partida
    jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).all()

    jugadores_info = []
    for jugador in jugadores:
        if jugador.id != player_id:
            jugador_info = {}
            jugador_info["nombre"] = jugador.nombre

            cartas_figura = get_cartasFigura_player(jugador.id, db)
            cartas_mov = get_cartasMovimiento_player(jugador.id, db)

            jugador_info["fig_cards"] = []
            for carta in cartas_figura:
                #Solo quiero enviar las cartas figura visibles
                if carta.estado == CardState.mano:
                    carta_info = {}
                    carta_info["id"] = carta.id
                    carta_info["fig"] = carta.figura.value
                    jugador_info["fig_cards"].append(carta_info)
            
            jugador_info["mov_cant"] = len(cartas_mov)

            jugadores_info.append(jugador_info)
    
    return jugadores_info