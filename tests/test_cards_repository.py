import pytest
import random
from sqlalchemy import create_engine, and_
from typing import List, Dict
from src.db import Base
from sqlalchemy.orm import sessionmaker
from src.models.partida import Partida
from src.models.inputs_front import *
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.repositories.cards_repository import *
from tests.test_helpers import test_db

#Helpers --

def cartas_mov_jugador_en_mano(jugador_id: int, test_db) -> List[MovementCard]:
    return test_db.query(MovementCard).filter(and_(MovementCard.jugador_id == jugador_id,
                                                MovementCard.estado == CardStateMov.mano)).all()

def cartas_mov_juego_en_mano(game_id: int, test_db) -> List[MovementCard]:
    return test_db.query(MovementCard).filter(and_(MovementCard.partida_id == game_id,
                                                MovementCard.estado == CardStateMov.mano)).all()

def cartas_fig_jugador_en_mano(jugador_id: int, test_db) -> List[PictureCard]: 
    return test_db.query(PictureCard).filter(and_(PictureCard.jugador_id == jugador_id,
                                        PictureCard.estado == CardState.mano)).all()

def cartas_fig_juego_en_mano(game_id: int, test_db) -> List[PictureCard]:
    return test_db.query(PictureCard).filter(and_(PictureCard.partida_id == game_id,
                                                PictureCard.estado == CardState.mano)).all()

def cartas_fig_en_juego(game_id: int, test_db) -> List[PictureCard]:
    return test_db.query(PictureCard).filter(PictureCard.partida_id == game_id).all()
# --

def test_repartir_cartas(test_db):
    partida = Partida(id=1, game_name = 'test', partida_iniciada = True, jugador_en_turno = 1, max_players=2)
    game_id = partida.id

    jugador1 = Jugador(id= 1, nombre='test',  es_anfitrion= True, turno= 1, partida_id = 1)
    jugador2 = Jugador(id= 2, nombre='test',  es_anfitrion= False, turno= 2, partida_id = 1)

    test_db.add(partida)
    test_db.add(jugador1)
    test_db.add(jugador2)
    test_db.commit()
    
    mezclar_cartas_movimiento(test_db, game_id)
    mezclar_figuras(game_id, test_db)

    cant_cartas_figura_en_juego_inicial = len(cartas_fig_en_juego(game_id, test_db)) 

    assert len(cartas_mov_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_jugador_en_mano(jugador1.id, test_db)) == 3
    
    repartir_cartas(game_id, test_db)
    
    assert len(cartas_mov_juego_en_mano(game_id, test_db)) == 6
    assert len(cartas_mov_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_jugador_en_mano(jugador1.id, test_db)) == 3

    cartas_movimiento_jugador1 = cartas_mov_jugador_en_mano(jugador1.id, test_db) 
    cartas_figura_jugador1 = cartas_fig_jugador_en_mano(jugador1.id, test_db)
    
    for i in range(2):
        cartaMov_jugador1 = cartas_movimiento_jugador1[i]            #El jugador hace 2 movimientos
        cartaMov_jugador1.estado = CardStateMov.descartada           #y arma una figura
        cartaFig_jugador1 = cartas_figura_jugador1
        test_db.commit()

    cartaFig_jugador1 = cartas_figura_jugador1[2]
    cartaFig_jugador1.partida_id = None
    cartaFig_jugador1.jugador_id = None
    test_db.delete(cartaFig_jugador1)
    test_db.commit()

    assert len(cartas_mov_jugador_en_mano(jugador1.id, test_db)) == 1
    assert len(cartas_fig_jugador_en_mano(jugador1.id, test_db)) == 2
    
    repartir_cartas(game_id, test_db)

    assert len(cartas_mov_juego_en_mano(game_id, test_db)) == 6
    assert len(cartas_mov_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_en_juego(game_id, test_db)) == cant_cartas_figura_en_juego_inicial - 1

    cartas_movimiento_jugador1 = cartas_mov_jugador_en_mano(jugador1.id, test_db)
    cartas_figura_jugador1 = cartas_fig_jugador_en_mano(jugador1.id, test_db)
    
    for i in range(3):
        cartaMov_jugador1 = cartas_movimiento_jugador1[i]            #El jugador hace 3 movimientos
        cartaMov_jugador1.estado = CardStateMov.descartada           #y forma dos figuras
        test_db.commit()

    for i in range(2):
        cartaFig_jugador1 = cartas_figura_jugador1[i]
        cartaFig_jugador1.partida_id = None
        cartaFig_jugador1.jugador_id = None
        test_db.delete(cartaFig_jugador1)
        test_db.commit()

    assert len(cartas_mov_jugador_en_mano(jugador1.id, test_db)) == 0
    assert len(cartas_fig_jugador_en_mano(jugador1.id, test_db)) == 1
    
    repartir_cartas(game_id, test_db)

    assert len(cartas_mov_juego_en_mano(game_id, test_db)) == 6
    assert len(cartas_mov_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_en_juego(game_id, test_db)) == cant_cartas_figura_en_juego_inicial - 3