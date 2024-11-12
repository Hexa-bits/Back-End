import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import status
from src.main import app
from src.routers.game import list_patterns
from sqlalchemy.exc import SQLAlchemyError, MultipleResultsFound
from sqlalchemy.orm import Session
from src.models.partida import Partida
from src.models.utils import *
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.utils import Coords
from typing import List
from src.game_helpers import BlockManager
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov

client = TestClient(app)


@patch("src.routers.game.game_manager")
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_CartaMovimiento")
@patch("src.routers.game.get_current_turn_player")
@patch("src.routers.game.is_valid_move")
@patch("src.routers.game.movimiento_parcial")
@patch("src.db.get_db")
def test_use_mov_card(mock_get_db, mock_mov_parcial, mock_is_valid, mock_get_current_turn,  
                     mock_get_movCard, mock_get_jugador, mock_game_manager):
    
    mock_jugador = MagicMock(id=1, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.return_value = mock_jugador
    mock_get_movCard.return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                movimiento= Move.diagonal_con_espacio,
                                                partida_id=1, jugador_id=1)
    mock_get_current_turn.return_value = mock_jugador
    mock_is_valid.return_value = True
    mock_mov_parcial.return_value = None
 
    response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                        "id_mov_card": 1,
                                                        "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                {"x_pos": 4, "y_pos": 4}]
                                                        })
        
    assert response.status_code == 200
    mock_game_manager.add_card_and_box_card.assert_called_once_with (1, 1, 
                                                                    (Coords(x_pos=2, y_pos=2), 
                                                                    Coords(x_pos=4, y_pos=4)))

@patch("src.routers.game.game_manager")
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_CartaMovimiento")
@patch("src.routers.game.get_current_turn_player")
@patch("src.routers.game.is_valid_move")
@patch("src.routers.game.movimiento_parcial")
@patch("src.db.get_db")
def test_use_mov_card_invalid_move(mock_get_db, mock_mov_parcial, mock_is_valid, mock_get_current_turn,  
                                    mock_get_movCard, mock_get_jugador, mock_game_manager):
    
    mock_jugador = MagicMock(id=1, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.return_value = mock_jugador
    mock_get_movCard.return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                movimiento= Move.diagonal_con_espacio,
                                                partida_id=1, jugador_id=1)
    mock_get_current_turn.return_value = mock_jugador
    mock_is_valid.return_value = False
    mock_mov_parcial.return_value = None

    response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                        "id_mov_card": 1,
                                                        "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                {"x_pos": 2, "y_pos": 3}]
                                                        })
                                
    assert response.status_code == 400
    assert response.json() == {'detail': "Movimiento invalido"}
    mock_game_manager.add_card_and_box_card.assert_not_called()

@patch("src.routers.game.game_manager")
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_CartaMovimiento")
@patch("src.routers.game.get_current_turn_player")
@patch("src.routers.game.is_valid_move")
@patch("src.routers.game.movimiento_parcial")
@patch("src.db.get_db")
def test_use_mov_card_invalid_card(mock_get_db, mock_mov_parcial, mock_is_valid, mock_get_current_turn,  
                                    mock_get_movCard, mock_get_jugador, mock_game_manager):
    
    mock_jugador = MagicMock(id=1, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.return_value = mock_jugador
    mock_get_movCard.return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                movimiento= Move.diagonal_con_espacio,
                                                partida_id=1, jugador_id=2)
    mock_get_current_turn.return_value = mock_jugador
    mock_is_valid.return_value = False
    mock_mov_parcial.return_value = None

    config = {
            "player_id": 1,
            "id_mov_card": 1,
            "fichas": [{"x_pos": 2, "y_pos": 2},
                        {"x_pos": 2, "y_pos": 3}]
            }
    response = client.put("/game/use-mov-card", json=config)
        
    assert response.status_code == 400
    assert response.json() == {'detail': "La carta no pertenece al jugador"}
    mock_game_manager.add_card_and_box_card.assert_not_called()

    mock_get_movCard.return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                movimiento= Move.diagonal_con_espacio,
                                                partida_id=2, jugador_id=1)

    response = client.put("/game/use-mov-card", json=config)
    
    assert response.status_code == 400
    assert response.json() == {'detail': "La carta no pertenece a la partida"}
    mock_game_manager.add_card_and_box_card.assert_not_called()

@patch("src.routers.game.game_manager")
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_CartaMovimiento")
@patch("src.routers.game.get_current_turn_player")
@patch("src.routers.game.is_valid_move")
@patch("src.routers.game.movimiento_parcial")
@patch("src.db.get_db")
def test_use_mov_card_invalid_player_or_not_in_hand(mock_get_db, mock_mov_parcial,
                                                    mock_is_valid, mock_get_current_turn,  
                                                    mock_get_movCard, mock_get_jugador,
                                                    mock_game_manager):

    mock_jugador1 = MagicMock(id=1, partida_id=1)
    mock_jugador2 = MagicMock(id=2, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.return_value = mock_jugador1
    mock_get_movCard.return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                movimiento= Move.diagonal_con_espacio,
                                                partida_id=1, jugador_id=2)
    mock_get_current_turn.return_value = mock_jugador2
    mock_is_valid.return_value = False
    mock_mov_parcial.return_value = None

    response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                        "id_mov_card": 1,
                                                        "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                {"x_pos": 2, "y_pos": 3}]
                                                        })
    assert response.status_code == 400
    assert response.json() == {'detail': "No es turno del jugador"}
    mock_game_manager.add_card_and_box_card.assert_not_called()

    mock_get_jugador.return_value = mock_jugador2
    mock_get_movCard.return_value = MovementCard(id=1, estado= CardStateMov.descartada, 
                                                movimiento= Move.diagonal_con_espacio,
                                                partida_id=1, jugador_id=2)

    response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                        "id_mov_card": 1,
                                                        "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                {"x_pos": 2, "y_pos": 3}]
                                                        })
        
    assert response.status_code == 400
    assert response.json() == {'detail': "La carta no está en mano"}
    mock_game_manager.add_card_and_box_card.assert_not_called()


@patch("src.routers.game.game_manager")
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_CartaMovimiento")
@patch("src.routers.game.get_current_turn_player")
@patch("src.routers.game.is_valid_move")
@patch("src.routers.game.movimiento_parcial")
@patch("src.db.get_db")
def test_use_mov_card_error(mock_get_db, mock_mov_parcial, mock_is_valid, mock_get_current_turn,  
                            mock_get_movCard, mock_get_jugador, mock_game_manager):
    
    mock_jugador = MagicMock(id=1, turno=0, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.return_value = mock_jugador
    mock_get_movCard.return_value = MovementCard(id=1, estado= CardStateMov.mano, 
                                                movimiento= Move.diagonal_con_espacio,
                                                partida_id=1, jugador_id=1)
    mock_get_current_turn.return_value = mock_jugador
    mock_is_valid.return_value = True
    mock_mov_parcial.side_effect = SQLAlchemyError

    response = client.put("/game/use-mov-card", json = {"player_id": 1,
                                                        "id_mov_card": 1,
                                                        "fichas": [{"x_pos": 2, "y_pos": 2},
                                                                {"x_pos": 4, "y_pos": 4}]
                                                        })
        
    assert response.status_code == 500
    assert response.json() == {'detail': "Fallo en la base de datos"}
    mock_game_manager.add_card_and_box_card.assert_not_called()

@patch('src.db.get_db')
@patch('src.routers.game.game_manager')
@patch("src.routers.game.get_Jugador")
@patch('src.routers.game.get_CartaFigura')
@patch('src.routers.game.get_current_turn_player')
@patch('src.routers.game.descartar_carta_figura')
@patch('src.routers.game.get_jugador_sin_cartas')
@patch('src.routers.game.block_manager')
@patch('src.routers.game.get_Partida')
@patch('src.routers.game.get_color_of_box_card')
@patch('src.routers.game.get_tablero')
def test_use_picture_card(mock_get_tablero,mock_get_color,mock_get_partida, mock_block_manager, mock_get_jugador_sin_cartas,
                          mock_descartar_carta, mock_get_jugador_turno, mock_get_carta, mock_get_jugador, mock_game_manager, 
                          mock_get_db):

    partida = MagicMock(id=1, winner_id=None)
    jugador = MagicMock(id=1, partida_id=1)
    figure = [{"x_pos": 1, "y_pos": 6}, {"x_pos": 2, "y_pos": 6}, {"x_pos": 2, "y_pos": 5}, 
              {"x_pos": 2, "y_pos": 4}, {"x_pos": 3, "y_pos": 4}]
    
    mock_get_tablero.return_value = MagicMock(color_prohibido=Color.VERDE)
    mock_get_color.return_value = Color.ROJO
    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida
    mock_get_jugador.return_value = jugador
    mock_get_carta.return_value = PictureCard(id=1, estado= CardState.mano, figura= Picture.figura10,
                                             partida_id=1, jugador_id=1)
    mock_get_jugador_turno.return_value = mock_get_jugador.return_value
    mock_descartar_carta.return_value = None
    mock_get_jugador_sin_cartas.return_value = None
    mock_block_manager.is_blocked.return_value = False

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})

    assert response.status_code == 200
    mock_game_manager.clean_cards_box_cards.assert_called()
    mock_block_manager.can_delete_blocked_card.assert_not_called()
    mock_block_manager.delete_other_card.assert_not_called()
    mock_block_manager.delete_blocked_card.assert_not_called()

@patch('src.db.get_db')
@patch('src.routers.game.game_manager')
@patch("src.routers.game.get_Jugador")
@patch('src.routers.game.get_CartaFigura')
@patch('src.routers.game.get_current_turn_player')
@patch('src.routers.game.descartar_carta_figura')
@patch('src.routers.game.get_jugador_sin_cartas')
@patch('src.routers.game.block_manager')
@patch("src.routers.game.unlock_player_figure_card")
@patch('src.routers.game.get_Partida')
@patch('src.routers.game.get_color_of_box_card')
@patch('src.routers.game.get_tablero')
def test_use_picture_card_unlock(mock_get_tablero,mock_get_color,mock_get_partida, mock_unlock_figure_card, mock_block_manager, 
                                 mock_get_jugador_sin_cartas, mock_descartar_carta, mock_get_jugador_turno,
                                 mock_get_carta, mock_get_jugador, mock_game_manager, mock_get_db):

    partida = MagicMock(id=1, winner_id=None)
    jugador = MagicMock(id=1, partida_id=1)
    figure = [{"x_pos": 1, "y_pos": 6}, {"x_pos": 2, "y_pos": 6}, {"x_pos": 2, "y_pos": 5},
              {"x_pos": 2, "y_pos": 4}, {"x_pos": 3, "y_pos": 4}]
    
    mock_get_tablero.return_value = MagicMock(color_prohibido=Color.VERDE)
    mock_get_color.return_value = Color.ROJO
    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida
    mock_get_jugador.return_value = jugador
    mock_get_carta.return_value = PictureCard(id=1, estado= CardState.mano, figura= Picture.figura10,
                                             partida_id=1, jugador_id=1)
    mock_get_jugador_turno.return_value = mock_get_jugador.return_value
    mock_descartar_carta.return_value = None
    mock_get_jugador_sin_cartas.return_value = None
    mock_block_manager.is_blocked.return_value = True
    mock_block_manager.can_delete_blocked_card.side_effect = [False, True]
    mock_block_manager.delete_other_card.return_value = None
    mock_block_manager.get_blocked_card_id.return_value = 2
    mock_unlock_figure_card.return_value = None

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})

    assert response.status_code == 200
    mock_game_manager.clean_cards_box_cards.assert_called_once()
    mock_block_manager.is_blocked.assert_called_once()
    mock_block_manager.can_delete_blocked_card.assert_called()
    mock_block_manager.delete_other_card.assert_called_once()
    mock_block_manager.delete_blocked_card.assert_not_called()
    mock_unlock_figure_card.assert_called_once()

@patch('src.db.get_db')
@patch('src.routers.game.game_manager')
@patch("src.routers.game.get_Jugador")
@patch('src.routers.game.get_CartaFigura')
@patch('src.routers.game.get_current_turn_player')
@patch('src.routers.game.descartar_carta_figura')
@patch('src.routers.game.get_jugador_sin_cartas')
@patch('src.routers.game.block_manager')
@patch("src.routers.game.unlock_player_figure_card")
@patch('src.routers.game.get_Partida')
@patch('src.routers.game.get_color_of_box_card')
@patch('src.routers.game.get_tablero')
def test_use_picture_card_delete_blocked(mock_get_tablero,mock_get_color,mock_get_partida, mock_unlock_figure_card,
                                        mock_block_manager, mock_get_jugador_sin_cartas, mock_descartar_carta, 
                                        mock_get_jugador_turno, mock_get_carta, mock_get_jugador, mock_game_manager, mock_get_db):

    partida = MagicMock(id=1, winner_id=None)
    jugador = MagicMock(id=1, partida_id=1)
    figure = [{"x_pos": 1, "y_pos": 6}, {"x_pos": 2, "y_pos": 6}, {"x_pos": 2, "y_pos": 5}, 
              {"x_pos": 2, "y_pos": 4}, {"x_pos": 3, "y_pos": 4}]
    
    mock_get_tablero.return_value = MagicMock(color_prohibido=Color.VERDE)
    mock_get_color.return_value = Color.ROJO
    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida
    mock_get_jugador.return_value = jugador
    mock_get_carta.return_value = PictureCard(id=1, estado= CardState.mano, figura= Picture.figura10,
                                             partida_id=1, jugador_id=1)
    mock_get_jugador_turno.return_value = mock_get_jugador.return_value
    mock_descartar_carta.return_value = None
    mock_get_jugador_sin_cartas.return_value = None
    mock_block_manager.is_blocked.return_value = True
    mock_block_manager.can_delete_blocked_card.return_value = True
    mock_block_manager.delete_other_card.return_value = None
    mock_block_manager.get_blocked_card_id.return_value = 2
    mock_unlock_figure_card.return_value = None

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})

    assert response.status_code == 200
    mock_game_manager.clean_cards_box_cards.assert_called_once()
    mock_block_manager.can_delete_blocked_card.assert_called_once()
    mock_block_manager.delete_other_card.assert_not_called()
    mock_block_manager.delete_blocked_card.assert_called_once()
    mock_unlock_figure_card.assert_not_called()


@patch('src.db.get_db')
@patch('src.routers.game.game_manager')
@patch("src.routers.game.get_Jugador")
@patch('src.routers.game.get_CartaFigura')
@patch('src.routers.game.get_current_turn_player')
@patch('src.routers.game.descartar_carta_figura')
@patch('src.routers.game.get_Partida')
@patch('src.routers.game.get_color_of_box_card')
@patch('src.routers.game.get_tablero')
def test_use_picture_card_invalid_card(mock_get_tablero,mock_get_color_of_box_card,mock_get_partida, mock_descartar_carta, mock_get_jugador_turno,
                                       mock_get_carta, mock_get_jugador, mock_game_manager, mock_get_db):

    partida = MagicMock(id=1, winner_id=None)
    jugador = MagicMock(id=1, partida_id=1)
    figure = [{"x_pos": 1, "y_pos": 6}, {"x_pos": 2, "y_pos": 6}, {"x_pos": 2, "y_pos": 5}, 
              {"x_pos": 2, "y_pos": 4}, {"x_pos": 3, "y_pos": 4}]

    mock_get_tablero.return_value = MagicMock(color_prohibido=Color.VERDE)
    mock_get_color_of_box_card.return_value = Color.ROJO.value
    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida
    mock_get_jugador.return_value = jugador
    mock_get_carta.return_value = PictureCard(id=1, estado= CardState.mano, figura= Picture.figura12,
                                              partida_id=1, jugador_id=1)    
    mock_get_jugador_turno.return_value = mock_get_jugador.return_value
    mock_descartar_carta.return_value = None

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})
    
    assert response.status_code == 400
    assert response.json() == {'detail': 'Figura invalida'}
    mock_game_manager.clean_cards_box_cards.assert_not_called()


@patch('src.db.get_db')
@patch('src.routers.game.game_manager')
@patch("src.routers.game.get_Jugador")
@patch('src.routers.game.get_CartaFigura')
@patch('src.routers.game.get_current_turn_player')
@patch('src.routers.game.descartar_carta_figura')
@patch('src.routers.game.get_Partida')
def test_use_picture_card_400_status_code(mock_get_partida, mock_descartar_carta, mock_get_jugador_turno,
                                          mock_get_carta, mock_get_jugador, mock_game_manager, mock_get_db):
    
    partida = MagicMock(id=1, winner_id=None)
    jugador1 = MagicMock(id=1, partida_id=1)
    jugador2 = MagicMock(id=2, partida_id=1)
    figure = [{"x_pos": 1, "y_pos": 6}, {"x_pos": 2, "y_pos": 6}, {"x_pos": 2, "y_pos": 5}, 
              {"x_pos": 2, "y_pos": 4}, {"x_pos": 3, "y_pos": 4}]
    
    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida
    mock_get_jugador.return_value = jugador1
    mock_get_carta.return_value = PictureCard(id=1, estado= CardState.mano, figura= Picture.figura10,
                                              partida_id=2)    
    mock_get_jugador_turno.return_value = mock_get_jugador.return_value
    mock_descartar_carta.return_value = None

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})
    
    assert response.status_code == 400
    assert response.json() == {'detail': 'La carta no pertenece a la partida'}

    mock_get_carta.return_value.partida_id = 1
    mock_get_carta.return_value.blocked = True

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})    

    assert response.status_code == 400
    assert response.json() == {"detail": "La carta esta bloqueada"}

    mock_get_carta.return_value.blocked = False
    mock_get_carta.return_value.jugador_id = 1
    mock_get_jugador_turno.return_value = jugador2

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})
    
    assert response.status_code == 400
    assert response.json() == {'detail': 'No es turno del jugador'}
    
    mock_get_jugador.return_value = mock_get_jugador_turno.return_value

    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})
    
    assert response.status_code == 400
    assert response.json() == {'detail': 'La carta no pertenece al jugador'}
    mock_game_manager.clean_cards_box_cards.assert_not_called()

@patch("src.routers.game.get_Jugador", side_effect = SQLAlchemyError)
def test_use_picture_card_error(mock_get_jugador):
    figure = [{"x_pos": 1, "y_pos": 6}, {"x_pos": 2, "y_pos": 6}, {"x_pos": 2, "y_pos": 5}, 
              {"x_pos": 2, "y_pos": 4}, {"x_pos": 3, "y_pos": 4}]
    response = client.put("/game/use-fig-card", json = {"player_id": 1, "id_fig_card": 1, "figura": figure})

    assert response.status_code == 500
    assert response.json() == {'detail': 'Fallo en la base de datos'}

@pytest.mark.asyncio
@patch("src.routers.game.get_valid_detected_figures")
@patch("src.routers.game.get_color_of_box_card")
@patch("src.db.get_db")
async def test_highlight_figures(mock_get_db, mock_get_color_of_box_card, mock_get_valid_detected_figures):
    # Crear un mock de la base de datos
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    # Mockear la lista de figuras detectadas que devuelve get_valid_detected_figures
    mock_figures = [
        [(0, 0), (0, 1)],  # Figura 1
        [(1, 1), (1, 2)]   # Figura 2
    ]
    mock_get_valid_detected_figures.return_value = mock_figures

    # Mockear la respuesta de get_color_of_ficha (color para cada ficha)
    mock_get_color_of_box_card.return_value = Color.ROJO.value

    # Parámetros para la llamada al endpoint
    game_id = 1
    response = client.get(f"/game/highlight-figures?game_id={game_id}")

    # Verificar el status code
    assert response.status_code == 200

    # Verificar la estructura de la respuesta
    expected_response = [
        [
            {'x': 1, 'y': 1, 'color': Color.ROJO.value},
            {'x': 1, 'y': 2, 'color': Color.ROJO.value}
        ],
        [
            {'x': 2, 'y': 2, 'color': Color.ROJO.value},
            {'x': 2, 'y': 3, 'color': Color.ROJO.value}
        ]
    ]
    assert response.json() == expected_response

@pytest.mark.asyncio
@patch("src.routers.game.get_valid_detected_figures")
@patch("src.db.get_db")
async def test_highlight_figures_db_error(mock_get_db, mock_get_valid_detected_figures):
    # Crear un mock de la base de datos
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    # Simular un error al obtener las figuras detectadas
    mock_get_valid_detected_figures.side_effect = Exception("Database error")

    # Parámetros para la llamada al endpoint
    game_id = 1
    response = client.get(f"/game/highlight-figures?game_id={game_id}")

    # Verificar que se devuelva un error 500
    assert response.status_code == 500

    # Verificar el contenido del mensaje de error
    assert response.json() == {"detail": "Error al obtener las figuras"}

@patch("src.routers.game.get_Partida")
@patch("src.routers.game.get_Jugador")
@patch("src.db.get_db")
def test_get_winner_OK_sin_cartas(mock_get_db, mock_get_jugador, 
                                 mock_get_partida):
    game_id = 1
    partida_mock = MagicMock(id=1, winner_id=1)
    jugadores_mock = [
                      MagicMock(id=1, nombre="testwinner", partida_id=1),
                      MagicMock(id=2, nombre="testlosser", partida_id=1)
                     ]

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida_mock
    mock_get_jugador.return_value = jugadores_mock [0]

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_partida.assert_called_once_with(game_id, ANY)
    mock_get_jugador.assert_called_once_with(partida_mock.winner_id, ANY)

    assert mock_get_jugador.return_value.id == partida_mock.winner_id
    assert response.status_code == 200
    assert response.json() == {"name_player": "testwinner"}


@patch("src.routers.game.get_Partida")
@patch("src.routers.game.get_Jugador")
@patch("src.db.get_db")
def test_get_winner_OK_abandonar(mock_get_db, mock_get_jugador, 
                                 mock_get_partida):
    game_id = 1
    partida_mock = MagicMock(id=1, winner_id=1)
    jugadores_mock = [MagicMock(id=1, nombre="testwinner", partida_id=1)]

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida_mock
    mock_get_jugador.return_value = jugadores_mock [0]

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_partida.assert_called_once_with(game_id, ANY)
    mock_get_jugador.assert_called_once_with(partida_mock.winner_id, ANY)

    assert mock_get_jugador.return_value.id == partida_mock.winner_id
    assert response.status_code == 200
    assert response.json() == {"name_player": "testwinner"}


@patch("src.routers.game.get_Partida")
@patch("src.routers.game.get_Jugador")
@patch("src.db.get_db")
def test_sql_except_winner (mock_get_db, mock_get_jugador, 
                            mock_get_partida):
    game_id = 1

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.side_effect = SQLAlchemyError()
    mock_get_jugador.return_value = None

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_partida.assert_called_once_with(game_id, ANY)
    mock_get_jugador.assert_not_called()
    assert response.status_code == 500
    assert response.json() == {"detail": "Fallo en la base de datos"}


@patch("src.routers.game.get_Partida")
@patch("src.routers.game.get_Jugador")
@patch("src.db.get_db")
def test_no_partida_except_winner(mock_get_db, mock_get_jugador, 
                                  mock_get_partida):    
    game_id = 1

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = None
    mock_get_jugador.side_effect = None

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_partida.assert_called_once_with(game_id, ANY)
    mock_get_jugador.assert_not_called()
    assert response.status_code == 404
    assert response.json() == {"detail": f"No existe la partida: {game_id}"}


@patch("src.routers.game.get_Partida")
@patch("src.routers.game.get_Jugador")
@patch("src.db.get_db")
def test_winner_BAD_request(mock_get_db, mock_get_jugador, 
                            mock_get_partida):    
    game_id = 1
    partida_mock = MagicMock(id=1, winner_id=None)
    
    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = partida_mock
    mock_get_jugador.return_value = None

    response = client.get(f"/game/get-winner?game_id={game_id}")

    mock_get_partida.assert_called_once_with(game_id, ANY)
    mock_get_jugador.assert_called_once_with(None, ANY)
    assert response.status_code == 400
    assert response.json() == {"detail": f"No hay ganador aún en partida: {game_id}"}

@pytest.mark.asyncio
@patch("src.routers.game.others_cards")  # Simula la función others_cards
@patch("src.db.get_db")  # Simula la dependencia de la base de datos
async def test_get_others_cards(mock_get_db, mock_others_cards):
    # Crear un mock de la base de datos
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    # Mockear la respuesta de others_cards
    mock_others_cards.return_value = [
        {
            "nombre": "Jugador 1",
            "fig_cards": [
                {"id": 1, "fig": "Figura 1"},
            ],
            "mov_cant": 2,
            "fig_cant": 3
        }
    ]

    # Parámetros para la llamada al endpoint
    game_id = 1
    player_id = 2
    response = client.get(f"/game/others-cards?game_id={game_id}&player_id={player_id}")

    # Verificar el status code
    assert response.status_code == 200

    # Verificar la estructura de la respuesta
    expected_response = [
        {
            "nombre": "Jugador 1",
            "fig_cards": [
                {"id": 1, "fig": "Figura 1"},
            ],
            "mov_cant": 2,
            "fig_cant": 3
        }
    ]
    assert response.json() == expected_response


@pytest.mark.asyncio
@patch("src.routers.game.others_cards")
@patch("src.db.get_db")
async def test_get_others_cards_db_error(mock_get_db, mock_others_cards):
    # Crear un mock de la base de datos
    mock_db = MagicMock(spec=Session)
    mock_get_db.return_value = mock_db

    # Simular un error en la función others_cards
    mock_others_cards.side_effect = Exception("Database error")

    # Parámetros para la llamada al endpoint
    game_id = 1
    player_id = 2
    response = client.get(f"/game/others-cards?game_id={game_id}&player_id={player_id}")

    # Verificar que se devuelva un error 500
    assert response.status_code == 500

    # Verificar el contenido del mensaje de error
    assert response.json() == {"detail": "Error al obtener las cartas de los demás jugadores"}
    
@pytest.mark.asyncio
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_Partida")
@patch("src.routers.game.game_manager")
@patch("src.routers.game.cancel_movement")
@patch("src.db.get_db")
async def test_cancelar_mov_OK(mock_get_db, mock_cancel_movimiento,
                                mock_manager, mock_get_partida, mock_get_jugador):
    #Inicializo elementos para la prueba
    mock_partida = MagicMock(id=1, jugador_en_turno=0, 
                             partida_empezada=True, winner_id=None)
    mock_jugador = MagicMock(id=1, turno=0, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = mock_partida
    mock_get_jugador.return_value = mock_jugador
    mock_cancel_movimiento.return_value = None

    coord1, coord2 = Coords(x_pos=1, y_pos=1), Coords(x_pos=2, y_pos=2)
    mock_manager.top_tuple_card_and_box_cards.return_value = (1, (coord1, coord2))
    mock_manager.pop_card_and_box_card.return_value = None

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_partida.assert_called_once_with(1, ANY)
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_manager.top_tuple_card_and_box_cards.assert_called_once_with(game_id=1)
    mock_cancel_movimiento.assert_called_with (mock_partida.id, mock_jugador.id, 
                                              1, (coord1, coord2), ANY)
    mock_manager.pop_card_and_box_card.assert_called_once_with(game_id=1)

    assert response.status_code == 204

@pytest.mark.asyncio
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_Partida")
@patch("src.routers.game.game_manager")
@patch("src.routers.game.cancel_movement")
@patch("src.db.get_db")
async def test_cancelar_mov_not_mov_parcial(mock_get_db, mock_cancel_movimiento,
                                          mock_manager, mock_get_partida, mock_get_jugador):
    #Inicializo elementos para la prueba
    mock_partida = MagicMock(id=1, jugador_en_turno=0, 
                             partida_empezada=True, winner_id=None)
    mock_jugador = MagicMock(id=1, turno=0, partida_id=1)

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_partida.return_value = mock_partida
    mock_get_jugador.return_value = mock_jugador
    mock_cancel_movimiento.return_value = None
    
    mock_manager.top_tuple_card_and_box_cards.return_value = None
    mock_manager.pop_card_and_box_card.return_value = None

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_partida.assert_called_once_with(1, ANY)
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_manager.top_tuple_card_and_box_cards.assert_called_once_with(game_id=1)
    mock_cancel_movimiento.assert_not_called()
    mock_manager.pop_card_and_box_card.assert_not_called()

    assert response.status_code == 400
    assert response.json() == {"detail": "No hay movimientos que deshacer"}

@pytest.mark.asyncio
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_Partida")
@patch("src.routers.game.game_manager")
@patch("src.routers.game.cancel_movement")
@patch("src.db.get_db")
async def test_cancelar_mov_not_jugador(mock_get_db, mock_cancel_movimiento,
                                        mock_manager, mock_get_partida, mock_get_jugador):
    #Inicializo elementos para la prueba
    mock_jugador = None

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.return_value = mock_jugador

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_get_partida.assert_not_called()
    mock_manager.top_tuple_card_and_box_cards.assert_not_called()
    mock_cancel_movimiento.assert_not_called()
    mock_manager.pop_card_and_box_card.assert_not_called()

    assert response.status_code == 404
    assert response.json() == {"detail": f'No existe el jugador: {config["player_id"]}'}

@pytest.mark.asyncio
@patch("src.routers.game.get_Jugador")
@patch("src.routers.game.get_Partida")
@patch("src.routers.game.game_manager")
@patch("src.routers.game.cancel_movement")
@patch("src.db.get_db")
async def test_cancelar_mov_sql_error(mock_get_db, mock_cancel_movimiento,
                                        mock_manager, mock_get_partida, mock_get_jugador):

    mock_get_db.return_value = MagicMock(spec=Session)
    mock_get_jugador.side_effect=SQLAlchemyError()

    config = {"game_id": 1, "player_id": 1}
    response = client.put("/game/cancel-mov", json=config)

    #Verifico que todo se llame como corresponde
    mock_get_jugador.assert_called_once_with(1, ANY)
    mock_get_partida.assert_not_called()
    mock_manager.top_tuple_card_and_box_cards.assert_not_called()
    mock_cancel_movimiento.assert_not_called()
    mock_manager.pop_card_and_box_card.assert_not_called()

    assert response.status_code == 500
    assert response.json() == {"detail": "Fallo en la base de datos"}

@pytest.mark.asyncio
async def test_block_figure_success(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")

    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})

    assert response.status_code == status.HTTP_200_OK



@pytest.mark.asyncio
async def test_block_figure_game_not_found(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= None)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")

    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No existe la partida"}


@pytest.mark.asyncio
async def test_block_figure_invalid_turn(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    #El jugador no esta en turno
    mock_game = MagicMock(id=1, jugador_en_turno=1, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")

    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "No es el turno del jugador"}


@pytest.mark.asyncio
async def test_block_figure_invalid_figure(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=False)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")

    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Figura invalida"}

@pytest.mark.asyncio
async def test_block_figure_no_player_to_block(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = None
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")

    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No existe el jugador a bloquear"}

@pytest.mark.asyncio
async def test_block_figure_already_blocked(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    #Ya esta bloqueado el jugador
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=True)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")


    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "El jugador ya está bloqueado"}

@pytest.mark.asyncio
async def test_block_figure_sql_error(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    #Fuerzo un error en la base de datos
    mocker.patch("src.routers.game.get_Jugador",side_effect=SQLAlchemyError)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")

    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "Fallo en la base de datos"}

@pytest.mark.asyncio
async def test_block_figure_not_card_figure(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = None
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.VERDE)
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block, mock_card_figura_2, mock_card_figura_3])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")


    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No existe la carta figura"}

@pytest.mark.asyncio
async def test_block_color_figure_block(mocker):
    mock_player = MagicMock(turno=0, partida_id=1)
    mock_game = MagicMock(id=1, jugador_en_turno=0, winner_id=None)
    mock_card_figura_block = MagicMock(id=1, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=1)
    mock_player_to_block = MagicMock(id=2, partida_id=1)
    mock_tablero = MagicMock(id=1, color_prohibido=Color.ROJO, partida_id=1)
    mock_card_figura_2 = MagicMock(id=2, estado=CardState.mano, figura=Picture.figura10, partida_id=1, jugador_id=2)
    mock_card_figura_3 = MagicMock(id=3, estado=CardState.mano, figura=Picture.figura11, partida_id=1, jugador_id=2)
    
    mocker.patch("src.routers.game.get_Jugador",side_effect=[mock_player, mock_player_to_block])
    mocker.patch("src.routers.game.get_Partida", return_value= mock_game)
    mocker.patch("src.routers.game.get_CartaFigura", return_value=mock_card_figura_block)
    mocker.patch("src.routers.game.is_valid_picture_card", return_value=True)
    mocker.patch("src.routers.game.get_tablero", return_value=mock_tablero)
    mocker.patch("src.routers.game.get_color_of_box_card", return_value=Color.ROJO)
    #Solo tengo una carta figura
    mocker.patch("src.routers.game.get_cartasFigura_player", return_value=[mock_card_figura_block])
    mocker.patch("src.routers.game.block_manager.is_blocked", return_value=False)
    mocker.patch("src.routers.game.block_player_figure_card")
    mocker.patch("src.routers.game.get_cards_not_blocked_id", return_value=[1, 2])
    mocker.patch("src.routers.game.block_manager.block_fig_card")
    mocker.patch("src.routers.game.game_manager.clean_cards_box_cards")
    mocker.patch("src.routers.game.ws_manager.send_message_game_id")    

    response = client.put("/game/block-fig-card", json={"player_id": 1, "id_fig_card": 1, "figura": [{"x_pos": 1, "y_pos": 1}]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "El color de la figura está prohibido"}
