import pytest
from sqlalchemy.exc import IntegrityError
from src.db import Base
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador
from src.models.inputs_front import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon

from src.consultas import mezclar_fichas

def test_mezclar_fichas(test_db):
    
    partida = Partida(game_name="partida", max_players=4)
    test_db.add(partida)
    test_db.commit()
    
    print(partida.id)
    
    #Creo un tablero y sus fichas mezcladas
    mezclar_fichas(test_db, partida.id)
    
    assert partida.tablero is not None
    
    tablero = test_db.query(Tablero).filter(Tablero.partida_id == partida.id).first()
    fichas = test_db.query(FichaCajon).filter(FichaCajon.tablero_id == tablero.id).all()
    
    assert len(fichas) == 36