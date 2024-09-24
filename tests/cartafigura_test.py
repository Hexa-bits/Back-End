import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from src.models.cartafigura import Picture, CardState, PictureCard 


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
    
    card = PictureCard(figura=Picture.figura1, estado=CardState.mano, partida_id=partida.id)
    
    # Añade la tarjeta a la base de datos
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    
    # Verifica que la tarjeta se haya añadido correctamente
    assert card.id is not None
    assert card.figura == Picture.figura1
    assert card.estado == CardState.mano

def test_picture_card_2(test_db):
    card = PictureCard(figura=Picture.figura2, estado=CardState.mazo)
    
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    assert card.partida_id is None
    assert card.id is not None
    assert card.figura == Picture.figura2
    assert (card.estado != CardState.mano) & (card.estado != CardState.bloqueada)    
    
    
def test_picture_card_repr(test_db):
    card = PictureCard(figura=Picture.figura3, estado=CardState.mazo)
    
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)

    expected_repr = f"id{card.id!r}, {card.figura!r}, {card.estado!r}"
    assert card.partida_id is None
    assert repr(card) == '{' + expected_repr + '}'

def test_picture_card_ids(test_db):
    card1 = PictureCard(figura=Picture.figura4, estado=CardState.mazo)
    card2 = PictureCard(figura=Picture.figura4, estado=CardState.mazo)
    
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
    
    card = PictureCard(figura=Picture.figura1, estado=CardState.mano, partida_id=partida.id)
    
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    card1 = PictureCard(figura=Picture.figura1, estado=CardState.mano, partida_id=partida.id)
    
    test_db.add(card1)
    test_db.commit()
    test_db.refresh(card1)
    
    assert card.partida_id == partida.id
    assert card1.partida_id == card.partida_id    
    