import unittest
from src.game import GameManager

class TestGameManager(unittest.TestCase):
    def setUp(self):
        """Se ejecuta antes de cada prueba, inicializando una instancia de GameManager."""
        self.game_manager = GameManager()
        self.game_id = 1  # Usamos un id de juego fijo para las pruebas
    
    def test_create_game(self):
        """Pruebo si el juego se crea correctamente."""
        self.game_manager.create_game(self.game_id)
        self.assertIn(self.game_id, self.game_manager.games)
        self.assertEqual(self.game_manager.games[self.game_id]['is_tablero_parcial'], False)
        self.assertEqual(self.game_manager.games[self.game_id]['cartas_y_fichas_usadas'], [])
        self.assertEqual(self.game_manager.games[self.game_id]['jugador_en_turno_id'], 0)

    def test_delete_game(self):
        """Pruebo si el juego se elimina correctamente."""
        self.game_manager.create_game(self.game_id)
        self.game_manager.delete_game(self.game_id)
        self.assertNotIn(self.game_id, self.game_manager.games)

    def test_apilar_carta_y_ficha(self):
        """Pruebo si apilar una carta y fichas convierte el tablero en parcial."""
        self.game_manager.create_game(self.game_id)
        self.game_manager.apilar_carta_y_ficha(self.game_id, 1, ((0, 0), (1, 1)))

        # Verificamos que la carta y fichas fueron apiladas
        self.assertEqual(self.game_manager.games[self.game_id]['cartas_y_fichas_usadas'], [(1, ((0, 0), (1, 1)))])
        # Verificamos que el tablero se convirtió en parcial
        self.assertTrue(self.game_manager.games[self.game_id]['is_tablero_parcial'])

    def test_desapilar_carta_y_ficha(self):
        """Pruebo si desapilar una carta y fichas convierte el tablero en real si el stack está vacío."""
        self.game_manager.create_game(self.game_id)
        self.game_manager.apilar_carta_y_ficha(self.game_id, 1, ((0, 0), (1, 1)))
        carta_ficha = self.game_manager.desapilar_carta_y_ficha(self.game_id)

        # Verificamos que se haya desapilado correctamente
        self.assertEqual(carta_ficha, (1, ((0, 0), (1, 1))))
        # Verificamos que el stack está vacío y el tablero es real
        self.assertEqual(self.game_manager.games[self.game_id]['cartas_y_fichas_usadas'], [])
        self.assertFalse(self.game_manager.games[self.game_id]['is_tablero_parcial'])

    def test_limpiar_cartas_fichas(self):
        """Pruebo si limpiar el stack convierte el tablero en real."""
        self.game_manager.create_game(self.game_id)
        self.game_manager.apilar_carta_y_ficha(self.game_id, 1, ((0, 0), (1, 1)))
        self.game_manager.limpiar_cartas_fichas(self.game_id)

        # Verificamos que el stack esté vacío y el tablero sea real
        self.assertEqual(self.game_manager.games[self.game_id]['cartas_y_fichas_usadas'], [])
        self.assertFalse(self.game_manager.games[self.game_id]['is_tablero_parcial'])

    def test_jugador_en_turno(self):
        """Pruebo si se obtiene y cambia el jugador en turno correctamente."""
        self.game_manager.create_game(self.game_id)
        self.game_manager.set_jugador_en_turno_id(self.game_id, 42)

        # Verificamos que el jugador en turno sea el correcto
        self.assertEqual(self.game_manager.obtener_jugador_en_turno_id(self.game_id), 42)


if __name__ == "__main__":
    unittest.main()
