import pytest
from sqlalchemy.exc import IntegrityError
from src.db import Base
from .test_helpers import test_db, cheq_entity
from src.models.jugadores import Jugador
from src.models.inputs_front import Partida_config
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard, CardState
from src.models.fichas_cajon import FichaCajon

from src.consultas import mezclar_cartas_movimiento

def test_mezclar_cartas_mov(test_db):

    partida = Partida(game_name="partida", max_players=4)
    test_db.add(partida)
    test_db.commit()
    
    jugador1 = Jugador(nombre="jugador1", es_anfitrion=True, partida_id=partida.id)
    test_db.add(jugador1)
    test_db.commit()
    
    jugador2 = Jugador(nombre="jugador2", es_anfitrion=False, partida_id=partida.id)
    test_db.add(jugador2)
    test_db.commit()
    
    jugador3 = Jugador(nombre="jugador3", es_anfitrion=False, partida_id=partida.id)
    test_db.add(jugador3)
    test_db.commit()
    
    jugador4 = Jugador(nombre="jugador4", es_anfitrion=False, partida_id=partida.id)
    test_db.add(jugador4)
    test_db.commit()
    
    #Creo las cartas de movimiento y 
    mezclar_cartas_movimiento(test_db, partida.id)
    
    #Chequeo que se hayan creado las cartas de movimiento
    cartas_mov = test_db.query(MovementCard).all()
    assert len(cartas_mov) == 49
    
    #Chequeo que todos los jugadores tengan 3 cartas mov
    jugadores = test_db.query(Jugador).all()
    for jugador in jugadores:
        assert len(jugador.cartasMovimiento) == 3
        
    #Chequeo que el resto esten en mazo
    mazo = test_db.query(MovementCard).filter(MovementCard.jugador_id == None).all()
    for carta in mazo:
        assert carta.estado == CardState.mazo
    
    #Chequo que hayan 49-(4*3) cartas en el mazo
    assert len(mazo) == 49-(4*3)
    
    
    