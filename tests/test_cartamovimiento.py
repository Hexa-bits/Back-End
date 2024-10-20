import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.models.jugadores import Jugador
from src.models.utils import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from src.models.cartamovimiento import Move, CardStateMov, MovementCard 


@pytest.fixture(scope='module')
def test_db():
    # Crea un motor de base de datos en memoria para pruebas
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    # Crea una sesión
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()

def test_picture_card_creation_and_relationship(test_db):
    partida = Partida(game_name="Mi partida", max_players=4)
    
    test_db.add(partida)
    test_db.commit()
    test_db.refresh(partida)
    
    card = MovementCard(movimiento=Move.diagonal_con_espacio, estado=CardStateMov.mano, partida_id=partida.id)
    
    # Añade la tarjeta a la base de datos
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    
    # Verifica que la tarjeta se haya añadido correctamente
    assert card.id is not None
    assert card.movimiento == Move.diagonal_con_espacio
    assert card.estado == CardStateMov.mano

def test_picture_card_2(test_db):
    card = MovementCard(movimiento=Move.diagonal_contiguo, estado=CardStateMov.mazo)
    
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    assert card.partida_id is None
    assert card.id is not None
    assert card.movimiento == Move.diagonal_contiguo
    assert (card.estado != CardStateMov.mano) & (card.estado != CardStateMov.descartada)    
    
    
def test_picture_card_repr(test_db):
    card = MovementCard(movimiento=Move.linea_al_lateral, estado=CardStateMov.descartada)
    
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)

    expected_repr = f"id{card.id!r}, {card.movimiento!r}, {card.estado!r}"
    assert card.partida_id is None
    assert repr(card) == '{' + expected_repr + '}'

def test_picture_card_ids(test_db):
    card1 = MovementCard(movimiento=Move.linea_con_espacio, estado=CardStateMov.mazo)
    card2 = MovementCard(movimiento=Move.linea_con_espacio, estado=CardStateMov.mazo)
    
    test_db.add(card1)
    test_db.commit()
    test_db.refresh(card1)

    test_db.add(card2)
    test_db.commit()
    test_db.refresh(card2)
    
    assert card1.id is not None
    assert card2.id is not None
    assert card1.id != card2.id 

def test_relationship2(test_db):
    partida = Partida(game_name="Mi partida", max_players=4)
    
    test_db.add(partida)
    test_db.commit()
    test_db.refresh(partida)
    
    card = MovementCard(movimiento=Move.L_derecha, estado=CardStateMov.mano, partida_id=partida.id)
    
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    card1 = MovementCard(movimiento=Move.L_izquierda, estado=CardStateMov.mano, partida_id=partida.id)
    
    test_db.add(card1)
    test_db.commit()
    test_db.refresh(card1)
    
    assert card.partida_id == partida.id
    assert card1.partida_id == card.partida_id