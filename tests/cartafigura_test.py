import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base
from sqlalchemy.orm import Session

from src.models.cartafigura import Picture, State, pictureCard 


@pytest.fixture(scope='module')
def test_db():
    # Crea un motor de base de datos en memoria para pruebas
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    # Crea una sesión
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()

def test_picture_card_creation(test_db):
    # Crea una instancia de pictureCard
    card = pictureCard(figura=Picture.figura1, estado=State.mano)
    
    # Añade la tarjeta a la base de datos
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    # Verifica que la tarjeta se haya añadido correctamente
    assert card.id is not None
    assert card.figura == Picture.figura1
    assert card.estado == State.mano

def test_picture_card_repr(test_db):
    card = pictureCard(figura=Picture.figura2, estado=State.mazo)
    
    test_db.add(card)
    test_db.commit()
    test_db.refresh(card)
    
    expected_repr = f"id={card.id!r}, figura={card.figura!r}, estado={card.estado!r}"
    assert repr(card) == expected_repr