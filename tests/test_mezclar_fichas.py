import pytest
from sqlalchemy.exc import IntegrityError
from src.db import Base
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador
from src.models.utils import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon

from src.repositories.board_repository import mezclar_box_cards

def test_mezclar_box_cards(test_db):
    
    partida = Partida(game_name="partida", max_players=4)
    test_db.add(partida)
    test_db.commit()
        
    #Creo un tablero y sus fichas mezcladas
    mezclar_box_cards(test_db, partida.id)
    
    assert partida.tablero is not None
    
    tablero = test_db.query(Tablero).filter(Tablero.partida_id == partida.id).first()
    box_cards = test_db.query(FichaCajon).filter(FichaCajon.tablero_id == tablero.id).all()
    
    assert len(box_cards) == 36