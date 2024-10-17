from unittest.mock import Mock, patch
import pytest
from sqlalchemy.orm import Session
from src.repositories.cards_repository import others_cards
from src.models.cartafigura import PictureCard, CardState
# Aquí asumimos que Jugador, PictureCard, MovementCard y CardState ya están importados

def test_others_cards():
    # Datos de prueba
    jugador_1 = Mock()
    jugador_1.id = 1
    jugador_1.nombre = "Jugador 1"

    jugador_2 = Mock()
    jugador_2.id = 2
    jugador_2.nombre = "Jugador 2"

    jugadores = [jugador_1, jugador_2]

    # Mock de las cartas de figura
    carta_figura_1 = Mock()
    carta_figura_1.id = 1
    carta_figura_1.figura.value = 1
    carta_figura_1.estado = CardState.mano  # Esta carta debe ser incluida

    carta_figura_2 = Mock()
    carta_figura_2.id = 2
    carta_figura_2.figura.value = 2
    carta_figura_2.estado = CardState.mazo  # Esta carta no debe ser incluida

    # Mock de las cartas de movimiento
    carta_movimiento_1 = Mock()

    # Mock de la base de datos
    db = Mock(spec=Session)
    db.query.return_value.filter.return_value.all.return_value = jugadores

    # Mock de las funciones que obtienen cartas
    with patch("src.repositories.cards_repository.get_cartasFigura_player") as mock_get_cartasFigura_player, \
         patch("src.repositories.cards_repository.get_cartasMovimiento_player") as mock_get_cartasMovimiento_player:

        mock_get_cartasFigura_player.side_effect = lambda player_id, db_session: [carta_figura_1, carta_figura_2] if player_id == jugador_1.id else []
        mock_get_cartasMovimiento_player.side_effect = lambda player_id, db_session: [carta_movimiento_1] if player_id == jugador_1.id else []

        # Llama a la función a testear
        resultado = others_cards(game_id=1, player_id=2, db=db)

        # Validaciones
        assert len(resultado) == 1
        assert resultado[0]["nombre"] == "Jugador 1"
        assert len(resultado[0]["fig_cards"]) == 1  # Solo la carta en estado "mano"
        assert resultado[0]["fig_cards"][0]["id"] == 1
        assert resultado[0]["fig_cards"][0]["fig"] == 1
        assert resultado[0]["mov_cant"] == 1
