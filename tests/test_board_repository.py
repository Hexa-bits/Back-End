import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.models.partida import Partida
from src.models.inputs_front import *
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.repositories.board_repository import movimiento_parcial
from typing import Any

def test_movimiento_parcial():
    mock_db = MagicMock()
    game_id = 1
    moveCard = MagicMock()
    moveCard.return_value = MovementCard(id= 1, estado= CardStateMov.mano)
    ficha0= Ficha(x_pos=1, y_pos=1)
    ficha1 = Ficha(x_pos=2, y_pos=2)
    coord = (ficha0, ficha1)
    
    # Simulando el comportamiento de las consultas
    mock_tablero = Tablero(id=1, partida_id=game_id)
    #mock_db_session.query.return_value.filter.return_value.first.return_value = mock_tablero
    
    mock_ficha0 = FichaCajon(x_pos=1, y_pos=1, color=Color.ROJO, tablero_id= 1)
    mock_ficha1 = FichaCajon(x_pos=2, y_pos=2, color=Color.AZUL, tablero_id= 1)

    #mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_ficha0, mock_ficha1]

    #with patch('src.repositories.board_repository.Session', side_effect = [mock_tablero, mock_ficha0, mock_ficha1]):

    movimiento_parcial(game_id, moveCard.return_value, coord, mock_db)

    assert mock_ficha0.color == Color.AZUL
    assert mock_ficha1.color == Color.ROJO
    assert moveCard.estado == CardStateMov.descartada
    