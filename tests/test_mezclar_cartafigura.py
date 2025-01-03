from src.main import app, mezclar_figuras
import pytest

from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .test_helpers import *
from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.utils import Partida_config
from src.models.tablero import Tablero
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from unittest.mock import ANY

from sqlalchemy.exc import IntegrityError

from tests.test_helpers import test_db

@patch("src.repositories.cards_repository.repartir_cartas_figuras")
def test_endpoint_mezclar_figuras_4players(mock_repartir_cartafigura, test_db):
    mock_repartir_cartafigura.side_effect = lambda game_id, figuras_list, db: mock_repartir_figuras(4, figuras_list)
    with patch("src.repositories.cards_repository.random.shuffle", side_effect=lambda x: x):
        mezclar_figuras (1, test_db)
        figuras_list = [x for x in range(1, 26)] + [x for x in range(1, 26)]

        mock_repartir_cartafigura.assert_called_once_with(1, figuras_list, ANY)


@patch("src.repositories.cards_repository.repartir_cartas_figuras")
def test_endpoint_mezclar_figuras_3players(mock_repartir_cartafigura, test_db):
    mock_repartir_cartafigura.side_effect = lambda game_id, figuras_list, db: mock_repartir_figuras(3, figuras_list)
    with patch("src.repositories.cards_repository.random.shuffle", side_effect=lambda x: x):
        mezclar_figuras (1,test_db)
        figuras_list = [x for x in range(1, 26)] + [x for x in range(1, 26)]

        mock_repartir_cartafigura.assert_called_once_with(1, figuras_list, ANY)


@patch("src.repositories.cards_repository.repartir_cartas_figuras")
def test_endpoint_mezclar_figuras_2players(mock_repartir_cartafigura, test_db):
    mock_repartir_cartafigura.side_effect = lambda game_id, figuras_list, db: mock_repartir_figuras(2, figuras_list)
    with patch("src.repositories.cards_repository.random.shuffle", side_effect=lambda x: x):
        mezclar_figuras (1, test_db)
        figuras_list = [x for x in range(1, 26)] + [x for x in range(1, 26)]

        mock_repartir_cartafigura.assert_called_once_with(1, figuras_list, ANY)