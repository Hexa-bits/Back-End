import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from src.repositories.cards_repository import *
from src.models.partida import Partida
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.cartamovimiento import MovementCard
from src.models.utils import Coords
from tests.test_helpers import test_db

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
