import pytest
from sqlalchemy.orm import Session
import random
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine, and_
from typing import List, Dict
from src.db import Base
from sqlalchemy.orm import sessionmaker
from src.models.partida import Partida
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.cartamovimiento import MovementCard
from src.models.utils import Coords
from tests.test_helpers import test_db
from src.models.utils import *
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.repositories.cards_repository import *
from tests.test_helpers import test_db


def test_others_cards():
    # Datos de prueba
    jugador_1 = Mock()
    jugador_1.id = 1
    jugador_1.nombre = "Jugador 1"

    jugador_2 = Mock()
    jugador_2.id = 2
    jugador_2.nombre = "Jugador 2"

    jugadores = [jugador_1, jugador_2]

    # Mock de las cartas de figura
    carta_figura_1 = Mock()
    carta_figura_1.id = 1
    carta_figura_1.figura.value = 1
    carta_figura_1.estado = CardState.mano  # Esta carta debe ser incluida

    carta_figura_2 = Mock()
    carta_figura_2.id = 2
    carta_figura_2.figura.value = 2
    carta_figura_2.estado = CardState.mazo  # Esta carta no debe ser incluida

    # Mock de las cartas de movimiento
    carta_movimiento_1 = Mock()

    # Mock de la base de datos
    db = Mock(spec=Session)
    db.query.return_value.filter.return_value.all.return_value = jugadores

    # Mock de las funciones que obtienen cartas
    with patch("src.repositories.cards_repository.get_cartasFigura_player") as mock_get_cartasFigura_player, \
         patch("src.repositories.cards_repository.get_cartasMovimiento_player") as mock_get_cartasMovimiento_player:

        mock_get_cartasFigura_player.side_effect = lambda player_id, db_session: [carta_figura_1, carta_figura_2] if player_id == jugador_1.id else []
        mock_get_cartasMovimiento_player.side_effect = lambda player_id, db_session: [carta_movimiento_1] if player_id == jugador_1.id else []

        # Llama a la función a testear
        resultado = others_cards(player_id=2, jugadores= jugadores, db=db)

        # Validaciones
        assert len(resultado) == 1
        assert resultado[0]["nombre"] == "Jugador 1"
        assert len(resultado[0]["fig_cards"]) == 1  # Solo la carta en estado "mano"
        assert resultado[0]["fig_cards"][0]["id"] == 1
        assert resultado[0]["fig_cards"][0]["fig"] == 1
        assert resultado[0]["mov_cant"] == 1


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
    
    #Testeo que se repartan las cartas correctamente con un jugador NO bloqueado
    player_blocked = False
    repartir_cartas(game_id,player_blocked, test_db)
    
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
    
    repartir_cartas(game_id, player_blocked, test_db)

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
    
    repartir_cartas(game_id,player_blocked, test_db)

    assert len(cartas_mov_juego_en_mano(game_id, test_db)) == 6
    assert len(cartas_mov_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_jugador_en_mano(jugador1.id, test_db)) == 3
    assert len(cartas_fig_en_juego(game_id, test_db)) == cant_cartas_figura_en_juego_inicial - 3

def test_descartar_carta_figura(test_db):
    jugador1 = Jugador(id=1, nombre="test", partida_id= 1)
    jugador2 = Jugador(id=2, nombre="test", partida_id= 1)
    partida = Partida(id=1, game_name= "test", max_players=2, partida_iniciada=True)
    
    test_db.add(partida)
    test_db.add(jugador1)
    test_db.add(jugador2)
    test_db.commit()

    carta_figura1 = PictureCard(id=1, estado = CardState.mano, partida_id = 1, jugador_id = 1)
    carta_figura2 = PictureCard(id=2, estado = CardState.mano, partida_id = 1, jugador_id = 1)
    carta_figura3 = PictureCard(id=3, estado = CardState.mano, partida_id = 1, jugador_id = 2)
    carta_figura4 = PictureCard(id=4, estado = CardState.mano, partida_id = 1, jugador_id = 2)

    test_db.add(carta_figura1)
    test_db.add(carta_figura2)
    test_db.add(carta_figura3)
    test_db.add(carta_figura4)
    test_db.commit()

    descartar_carta_figura(1, test_db)

    assert get_cartasFigura_player(jugador1.id, test_db) == [carta_figura2]
    assert get_CartaFigura(1, test_db) == None

    descartar_carta_figura(3, test_db)
    descartar_carta_figura(4, test_db)

    assert get_cartasFigura_player(jugador2.id, test_db) == []
    assert get_CartaFigura(3, test_db) == None
    assert get_CartaFigura(4, test_db) == None

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

@patch("src.repositories.cards_repository.swap_box_card")
def test_cancel_movement_OK(mock_swap, movs_test):
    """
    Testeo que la función cancel_movement funcione correctamente con los 
    parametros adecuados.
    """
    mock_swap.return_value = None
    tuple_coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))

    result = cancel_movement(1, 1, 1, tuple_coords, movs_test)
    assert result is None, f'No devuelve None, sino {result}'

    mov_card = get_cartaMovId(1, movs_test)
    assert mov_card is not None, "'mov_card' no debería de ser None"
    assert isinstance(mov_card, MovementCard), f'El tipo no debería ser {type(mov_card)}'
    assert mov_card.estado == CardStateMov.mano, f'La carta esta en {mov_card.estado}'
    assert mov_card.jugador_id == 1, "No tiene el jugador asoc esperado"
    assert mov_card.partida_id == 1, "No tiene la partida asoc esperada"

@patch("src.repositories.cards_repository.swap_box_card")
def test_cancel_movement_not_in_db(mock_swap, movs_test):
    """
    Testeo que la función cancel_movement falle si es que no existe la carta de
    movimiento en la db.  
    """
    mock_swap.return_value = None
    tuple_coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))

    with pytest.raises(ValueError, match="La carta de movimiento no existe en la partida"):
        cancel_movement(1, 1, 0, tuple_coords, movs_test)

@patch("src.repositories.cards_repository.swap_box_card")
def test_cancel_movement_mov_mano(mock_swap, movs_test):
    """
    Testeo que la función cancel_movement falle si es la carta de movimiento esta
    en mano.
    """
    mock_swap.return_value = None
    tuple_coords = (Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2))

    with pytest.raises(ValueError, match="La carta de movimiento esta en mano de alguien"):
        cancel_movement(1, 1, 2, tuple_coords, movs_test)

@patch("src.repositories.cards_repository.swap_box_card")
def test_movimiento_parcial(mock_swap, movs_test):

    mock_swap.return_value = None
    
    box_card0 = Coords(x_pos = 1, y_pos = 1)
    box_card1 = Coords(x_pos = 2, y_pos = 2)
    coord = (box_card0, box_card1)
    moveCard = get_cartaMovId(1, movs_test)

    assert moveCard is not None

    movimiento_parcial(1, moveCard, coord, movs_test)

    assert moveCard.estado == CardStateMov.descartada
    assert moveCard.jugador_id == None


def test_block_player_figure_card(test_db):
    jugador = Jugador(id=1, nombre="test", partida_id=1)
    carta_figura = PictureCard(id=1, estado=CardState.mano, partida_id=1, jugador_id=1)

    test_db.add(jugador)
    test_db.add(carta_figura)
    test_db.commit()

    block_player_figure_card( 1, test_db)

    assert get_CartaFigura(1, test_db).blocked == True

def test_unlock_player_figure_card(test_db):
    player = Jugador(id=1, nombre="test", partida_id=1)
    figure_card = PictureCard(id=1, estado=CardState.mano, partida_id=1, jugador_id=1)

    test_db.add(player)
    test_db.add(figure_card)
    test_db.commit()

    unlock_player_figure_card(1, test_db)

    assert get_CartaFigura(1, test_db).blocked == False