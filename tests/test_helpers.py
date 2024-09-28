import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.models.partida import Partida
from src.models.jugadores import Jugador
from src.consultas import *
from src.models.cartafigura import PictureCard, Picture, CardState
from src.models.inputs_front import Partida_config
from typing import List


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
    

def mock_delete_players_partida(max_players: int):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        db_prueba(max_players, test_db)
        partida = get_Partida(1, test_db)
        delete_players_partida(partida, test_db)
        assert player_in_partida(partida, test_db) == 0 


def mock_delete_player(max_players: int):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        db_prueba(max_players, test_db)
        jugador = get_Jugador(1, test_db)
        partida = get_Partida(jugador.partida_id, test_db)
        delete_player(jugador, test_db)

        assert player_in_partida(partida, test_db) == (0 if partida.partida_iniciada and max_players <= 2 else max_players - 1)
        assert jugador.partida_id == None


def mock_repartir_figuras(max_players: int, figuras_list: List[int]):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    
    with (SessionLocal() as test_db):
        db_prueba(max_players, test_db)
        repartir_cartas_figuras(game_id=1, figuras_list=figuras_list, db=test_db)

        for i in range(1, max_players+1):
            cartas = get_cartasFigura_player(i, test_db)
            assert len(cartas) == 50//max_players
            assert len([x for x in cartas if x.estado == CardState.mano]) == 3

            
def db_prueba(max_players: int, db: Session):
    try:
        partida = Partida(game_name="partida", max_players=max_players)
        db.add(partida)
        db.commit()
        db.refresh(partida)
        for i in range(0, max_players):
            jugador = Jugador(nombre=f'player_{i}', turno=i+1)
            jugador.partida_id = partida.id
            db.add(jugador)
        db.commit()
    except SQLAlchemyError:
        db.rollback()


def mock_list_fig_cards (figura: Picture) -> List[int]:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with (SessionLocal() as test_db):
        jugador = Jugador(nombre="player")
        test_db.add(jugador)
        test_db.commit()
        test_db.refresh(jugador)

        mov_card = PictureCard(figura=figura, estado=CardState.mano)
        mov_card.jugador_id = jugador.id
        test_db.add(mov_card)
        test_db.commit()

        cards = list_fig_cards(jugador.id, test_db)

        assert cards is not None
        return cards