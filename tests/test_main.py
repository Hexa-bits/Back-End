import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.main import app, lista_patrones
from src.models.fichas_cajon import Color

client = TestClient(app)

@pytest.mark.asyncio
@patch("src.main.get_valid_detected_figures")
@patch("src.main.get_color_of_ficha")
@patch("src.main.get_db")
async def test_highlight_figures(mock_get_db, mock_get_color_of_ficha, mock_get_valid_detected_figures):
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
    mock_get_color_of_ficha.return_value = Color.ROJO.value

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
@patch("src.main.get_valid_detected_figures")
@patch("src.main.get_db")
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

@pytest.mark.asyncio
@patch("src.main.others_cards")  # Simula la función others_cards
@patch("src.main.get_db")  # Simula la dependencia de la base de datos
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
            "mov_cant": 2
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
            "mov_cant": 2
        }
    ]
    assert response.json() == expected_response


@pytest.mark.asyncio
@patch("src.main.others_cards")
@patch("src.main.get_db")
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