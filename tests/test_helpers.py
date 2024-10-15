import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from src.db import Base
from src.models.partida import Partida
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, Picture, CardState
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.models.tablero import Tablero
from src.models.color_enum import Color
from src.models.fichas_cajon import FichaCajon
from src.models.utils import Partida_config
from typing import List

from src.repositories.cards_repository import get_cartasFigura_player, list_fig_cards, list_mov_cards, repartir_cartas_figuras
from src.repositories.game_repository import  get_Partida
from src.repositories.player_repository import add_partida
from src.repositories.player_repository import delete_player, delete_players_partida, get_Jugador, player_in_partida


@pytest.fixture(scope='function')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        yield db


def cheq_entity(entity: object, dicc: dict) -> bool:
    res = True
    for (key, des) in dicc.items():
        atributo = getattr(entity, key, None)
        res = atributo == des
        if (not res):
            break
    return res 


def mock_add_partida(config: Partida_config) -> int:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        jugador = Jugador(nombre="player")
        test_db.add(jugador)
        test_db.commit()

        id_game = add_partida(config, test_db)
        test_db.refresh(jugador)

        assert jugador.partida_id == id_game
        assert jugador.partida.game_name == config.game_name
        assert jugador.partida.max_players == config.max_players

        return id_game 
    

def mock_delete_players_partida(max_players: int, empezada: bool):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        db_prueba(max_players, empezada, test_db)
        partida = get_Partida(1, test_db)
        delete_players_partida(partida, test_db)
        assert player_in_partida(partida, test_db) == 0 


def mock_delete_player(max_players: int, empezada: bool):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        db_prueba(max_players, empezada, test_db)
        jugador = get_Jugador(1, test_db)
        partida = get_Partida(jugador.partida_id, test_db)
        delete_player(jugador, test_db)

        assert player_in_partida(partida, test_db) == (0 if partida.partida_iniciada and max_players == 1 else max_players - 1)
        assert jugador.partida_id == None


def mock_repartir_figuras(max_players: int, figuras_list: List[int]):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    
    with (SessionLocal() as test_db):
        db_prueba(max_players, True, test_db)
        repartir_cartas_figuras(game_id=1, figuras_list=figuras_list, db=test_db)

        for i in range(1, max_players+1):
            cartas = get_cartasFigura_player(i, test_db)
            assert len(cartas) == 50//max_players
            assert len([x for x in cartas if x.estado == CardState.mano]) == 3            
        

def db_prueba(max_players: int, emepezada: bool, db: Session):
    try:
        partida = Partida(game_name="partida", max_players=max_players, partida_iniciada=emepezada)
        db.add(partida)
        db.flush()
        for i in range(0, max_players):
            jugador = Jugador(nombre=f'player_{i}', turno=i+1)
            jugador.partida_id = partida.id
            db.add(jugador)
        
        if (emepezada):
            partida.jugador_en_turno = 1
            tablero = Tablero()
            tablero.partida_id = partida.id
            db.add(tablero)
            db.flush()

            colores = [Color.ROJO]*9 + [Color.VERDE]*9 + [Color.AMARILLO]*9 + [Color.AZUL]*9
            coordenadas = [(x, y) for x in range(1, 7) for y in range(1, 7)]
            for coord in coordenadas:
                x, y = coord
                color = colores.pop()
                ficha = FichaCajon(x_pos=x, y_pos=y, color=color, tablero_id=tablero.id)
                db.add(ficha)

        db.commit()
    except SQLAlchemyError:
        db.rollback()


def mock_list_mov_cards (mov_cards: List[MovementCard]) -> List[int]:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        jugador = Jugador(nombre="player")
        test_db.add(jugador)
        test_db.commit()
        test_db.refresh(jugador)

        for mov_card in mov_cards:
            mov_card.jugador_id = jugador.id
            test_db.add(mov_card)

        test_db.commit()

        cards = list_mov_cards(jugador.id, test_db)

        assert cards is not None
        return cards

def mock_list_fig_cards (fig_cards: List[PictureCard]) -> List[int]:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        jugador = Jugador(nombre="player")
        test_db.add(jugador)
        test_db.commit()
        test_db.refresh(jugador)

        for fig_card in fig_cards:
            fig_card.jugador_id = jugador.id
            test_db.add(fig_card)
        test_db.commit()

        cards = list_fig_cards(jugador.id, test_db)

        assert cards is not None
        return cards

