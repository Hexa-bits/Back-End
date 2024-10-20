import pytest
import random
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, and_
from typing import List, Dict
from src.db import Base
from sqlalchemy.orm import sessionmaker
from src.models.partida import Partida
from src.models.utils import *
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

@pytest.fixture
def movs_test(test_db: Session) -> Session:
    """Inyección de base de datos de prueba para cada test."""
    
    partida = Partida(id=1, game_name="partida", max_players=4, partida_iniciada=True)
    jugador = Jugador(id=1, nombre="player", partida_id=1)
    
    mov_card1 = MovementCard(id=1, movimiento=Move.diagonal_con_espacio, 
                             estado=CardStateMov.descartada, partida_id=1)
    mov_card2 = MovementCard(id=2, movimiento=Move.diagonal_con_espacio, 
                             estado=CardStateMov.mano, partida_id=1, jugador_id=1)

    test_db.add_all([partida, jugador, jugador, mov_card1, mov_card2])
    test_db.commit()
    return test_db

@patch("src.repositories.cards_repository.swap_fichasCajon")
def test_cancelar_movimiento_OK(mock_swap, movs_test):
    """
    Testeo que la función cancelar_movimiento funcione correctamente con los 
    parametros adecuados.
    """
    mock_swap.return_value = None
    tupla_coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))

    result = cancelar_movimiento(1, 1, 1, tupla_coords, movs_test)
    assert result is None, f'No devuelve None, sino {result}'

    mov_card = get_cartaMovId(1, movs_test)
    assert mov_card is not None, "'mov_card' no debería de ser None"
    assert isinstance(mov_card, MovementCard), f'El tipo no debería ser {type(mov_card)}'
    assert mov_card.estado == CardStateMov.mano, f'La carta esta en {mov_card.estado}'
    assert mov_card.jugador_id == 1, "No tiene el jugador asoc esperado"
    assert mov_card.partida_id == 1, "No tiene la partida asoc esperada"

@patch("src.repositories.cards_repository.swap_fichasCajon")
def test_cancelar_movimiento_not_in_db(mock_swap, movs_test):
    """
    Testeo que la función cancelar_movimiento falle si es que no existe la carta de
    movimiento en la db.  
    """
    mock_swap.return_value = None
    tupla_coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))

    with pytest.raises(ValueError, match="La carta de movimiento no existe en la partida"):
        cancelar_movimiento(1, 1, 0, tupla_coords, movs_test)

@patch("src.repositories.cards_repository.swap_fichasCajon")
def test_cancelar_movimiento_mov_mano(mock_swap, movs_test):
    """
    Testeo que la función cancelar_movimiento falle si es la carta de movimiento esta
    en mano.
    """
    mock_swap.return_value = None
    tupla_coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))

    with pytest.raises(ValueError, match="La carta de movimiento esta en mano de alguien"):
        cancelar_movimiento(1, 1, 2, tupla_coords, movs_test)

@patch("src.repositories.cards_repository.swap_fichasCajon")
def test_movimiento_parcial(mock_swap, movs_test):

    mock_swap.return_value = None
    
    ficha0 = Coords(x_pos = 1, y_pos = 1)
    ficha1 = Coords(x_pos = 2, y_pos = 2)
    coord = (ficha0, ficha1)
    moveCard = get_cartaMovId(1, movs_test)

    assert moveCard is not None

    movimiento_parcial(1, moveCard, coord, movs_test)

    assert moveCard.estado == CardStateMov.descartada
    assert moveCard.jugador_id == None
