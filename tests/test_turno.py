import pytest
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon
import unittest
from unittest.mock import MagicMock, patch, ANY
from src.repositories.player_repository import asignar_turnos
import pdb

class TestAsignarTurnos(unittest.TestCase):

    @patch('src.consultas.get_jugadores')
    def test_asignar_turnos(self, mock_get_jugadores):
        # Configuración del mock
        mock_db = MagicMock()  # Crea un mock para la base de datos
        game_id = 1
        jugadores_mock = [
            MagicMock(turno=None),  # Jugador 1
            MagicMock(turno=None),  # Jugador 2
            MagicMock(turno=None)   # Jugador 3
        ]
        
        mock_get_jugadores.return_value = jugadores_mock
            
        asignar_turnos(game_id, mock_db)

        for jugador in jugadores_mock:
            self.assertIsNotNone(jugador.turno)
            
        
        self.assertEqual(mock_db.commit.call_count, len(jugadores_mock))
        self.assertEqual(mock_db.refresh.call_count, len(jugadores_mock))

    @patch('src.consultas.get_jugadores')
    def test_asignar_turnos1(self, mock_get_jugadores):
        mock_db = MagicMock()
        game_id = 1
        jugadores_mock = [
            MagicMock(id=1, turno=None), 
            MagicMock(id=2, turno=None),  
            MagicMock(id=3, turno=None) 
        ]
        
        mock_get_jugadores.return_value = jugadores_mock
        with patch('random.sample', return_value= [2,0,1]):
            asignar_turnos(game_id, mock_db)

            for jugador in jugadores_mock:
                self.assertIsNotNone(jugador.turno)
                if (jugador.id==1):
                    self.assertEqual(jugador.turno, 2)
                if (jugador.id==2):
                    self.assertEqual(jugador.turno, 0)
                if (jugador.id==3):
                    self.assertEqual(jugador.turno, 1)

if __name__ == '__main__':
    unittest.main()

