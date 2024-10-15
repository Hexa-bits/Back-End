"""
Este tests verfica la funcionalidad de función cancelar_movimiento, misma
que swapea las fichasCajon de una partida y retorna una carta de movimiento
indicada a la mano de un jugador. 
"""

import unittest
import pytest
from sqlalchemy.orm import Session
from .test_helpers import test_db
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.tablero import Tablero
from src.models.cartamovimiento import *
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.utils import Coords
from src.repositories.board_repository import mezclar_fichas, get_fichaCajon_coords, swap_fichasCajon
from src.repositories.game_repository import terminar_turno, cancelar_movimiento
from src.repositories.cards_repository import get_cartaMovId
from unittest.mock import patch, MagicMock


class TestCancelMov(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_test_db(self, test_db: Session):
        """
        Inyecto una db de prueba local (vive en el alcance del test) en cada
        unnitest, esta luego se setea a conveniencia en SetUp (inicialización).
        """
        self.test_db = test_db

    def setUp(self):
        """
        Inicializo los parametros de prueba del test y la base de datos local
        por cada unnitest.
        """
        #Pueblo la base de datos local
        partida = Partida(id=1, game_name="partida", max_players=4, partida_iniciada=True)
        jugador = Jugador(id=1, nombre="player", partida_id=1)

        tablero = Tablero(id=1, partida_id=1)
        
        mov_card1 = MovementCard(id=1, movimiento=Move.diagonal_con_espacio, 
                                estado=CardStateMov.descartada, partida_id=1)
        mov_card2 = MovementCard(id=2, movimiento=Move.diagonal_con_espacio, 
                                estado=CardStateMov.mano, partida_id=1, jugador_id=1)
        
        ficha1 = FichaCajon(id=1, x_pos=1, y_pos=1, color=Color.ROJO, tablero_id=1)
        ficha2 = FichaCajon(id=2, x_pos=2, y_pos=2, color=Color.VERDE, tablero_id=1)

        self.test_db.add_all ([partida, jugador, tablero, mov_card1, mov_card2, ficha1, ficha2])
        self.test_db.commit()
        
        #Seteo los parametros de prueba
        self.partida = MagicMock()
        self.jugador = MagicMock()
        self.initial_fichas = (ficha1, ficha2)
    
    def test_switch_cartasCajon_OK(self):
        """
        Testeo que la función swap_fichasCajon funcione correctamente con los 
        parametros adecuados.
        """
        self.partida.id = 1
        self.jugador.id = 1
        tupla_coords = (Coords(x=1, y=1), Coords(x=2, y=2))

        try:
            result = swap_fichasCajon(self.partida.id, tupla_coords, self.test_db)
        
        except Exception as e:
            # Verifico que la transacción no lance una excepción
            self.fail(f'La función lanzó una exc innesperada: {e}')
        
        #Verifico que el resultado sea None
        self.assertIsNone(result, f'No devuelve None, sino {result}')

        #Obtengo las fichasCajon que la db de prueba
        ficha1 = get_fichaCajon_coords(self.partida.id, tupla_coords[0], self.test_db)
        ficha2 = get_fichaCajon_coords(self.partida.id, tupla_coords[1], self.test_db)

        #Verifico que las consultas devuelvan una fichaCajon        
        self.assertIsNotNone(ficha1)
        self.assertIsNotNone(ficha2)
        self.assertIsInstance(ficha1, FichaCajon, 
                              f'El tipo no debería ser {type(ficha1)}')
        self.assertIsInstance(ficha2, FichaCajon,
                             f'El tipo no debería ser {type(ficha1)}')

        #Verfico que las fichas se hayan swappeado, comparandolas con sus instancias previas
        self.assertEqual(ficha1, self.initial_fichas[0],
                          f'No se intercambian fichas')
        self.assertEqual(ficha2, self.initial_fichas[1],
                          f'No se intercambian fichas')

    def test_switch_cartasCajon_not_in_db(self):
        """
        Testeo que la función swap_fichasCajon falle si es que el trata de obtener la info
        de una partida que no existe 
        """
        self.partida.id = 2
        self.jugador.id = 2
        tupla_coords = (Coords(x=1, y=1), Coords(x=2, y=2))

        with self.assertRaises(Exception) as context:
            swap_fichasCajon(self.partida.id, tupla_coords, self.test_db)

        self.assertEqual(str(context.exception), 
                        "Una o ambas fichasCajon no existe en la db")
        
    def test_switch_cartasCajon_null_param(self):
        """
        Testeo que la función swap_fichasCajon falle si es que se pasan parametros
        None 
        """
        with self.assertRaises(TypeError):
            swap_fichasCajon(None, None, self.test_db)
    
    def test_cancelar_movimiento_OK(self):
        """
        Testeo que la función cancelar_movimiento funcione correctamente con los 
        parametros adecuados.
        """
        self.partida.id = 1
        self.jugador.id = 1
        tupla_coords = (Coords(x=1, y=1), Coords(x=2, y=2))

        try:
            result = cancelar_movimiento(partida=self.partida,
                                         jugador=self.jugador,
                                         mov_id=1,
                                         tupla_coords=tupla_coords,
                                         db=self.test_db)
        
        except Exception as e:
            self.fail(f'La función lanzó una exc innesperada: {e}')
        
        self.assertIsNone(result, f'No devuelve None, sino {result}')

        # Verifico que la carta se devuelva a la mano, al jugador indicado
        mov_card = get_cartaMovId(1, self.test_db)
        self.assertIsNotNone(mov_card, f'No debería ser None')
        self.assertIsInstance(mov_card, MovementCard, 
                              f'El tipo no debería ser {type(mov_card)}')
        self.assertEqual(mov_card.estado, CardStateMov.mano, 
                        f'La carta esta en {mov_card.estado}')
        self.assertEqual(mov_card.jugador_id, self.jugador.id, 
                        f'La carta esta asociada al jugador {mov_card.jugador_id}')
        self.assertEqual(mov_card.partida_id, self.partida.id,
                        f'La carta esta asociada a la partida {mov_card.partida_id}')
    
    def test_cancelar_movimiento_not_in_db(self):
        """
        Testeo que la función cancelar_movimiento falle si es que no existe la carta de
        movimiento en la db.  
        """
        self.partida.id = 1
        self.jugador.id = 1
        tupla_coords = (Coords(x=1, y=1), Coords(x=2, y=2))

        with self.assertRaises(Exception) as context:
            cancelar_movimiento(partida=self.partida,
                                jugador=self.jugador,
                                mov_id=0,
                                tupla_coords=tupla_coords,
                                db=self.test_db)

        self.assertEqual(str(context.exception), 
                        "La carta de movimiento no existe en la partida")
    
    def test_cancelar_movimiento_mov_mano(self):
        """
        Testeo que la función cancelar_movimiento falle si es la carta de movimiento esta
        en mano.
        """
        self.partida.id = 1
        self.jugador.id = 1
        tupla_coords = (Coords(x=1, y=1), Coords(x=2, y=2))

        with self.assertRaises(Exception) as context:
            cancelar_movimiento(partida=self.partida,
                                jugador=self.jugador,
                                mov_id=2,
                                tupla_coords=tupla_coords,
                                db=self.test_db)

        self.assertEqual(str(context.exception), 
                        "La carta de movimiento esta en mano")

if __name__ == "__main__":
    unittest.main()