import pytest
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
from unittest.mock import MagicMock, patch, ANY
from src.consultas import asignar_turnos
import pdb

def test_turno():
    with patch('src.consultas.random') as mock_random:
        with patch('src.consultas.get_jugadores') as mock_query:
                mock_random.return_value = [1, 0, 2]
            
                jugador1_mock = MagicMock()
                jugador2_mock = MagicMock()
                jugador3_mock = MagicMock()
                jugador1_mock.return_value = Jugador(id= 1, nombre= 'test', partida_id=1)
                jugador2_mock.return_value = Jugador(id= 2, nombre= 'test', partida_id=1)
                jugador3_mock.return_value = Jugador(id= 3, nombre= 'test', partida_id=1)
                mock_query.return_value = [(jugador1_mock.return_value), (jugador2_mock.return_value), (jugador3_mock.return_value)]
                result = asignar_turnos(1, ANY)
                assert result == [(1,1), (2,0), (3,2)]
