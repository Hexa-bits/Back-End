import pytest
from unittest.mock import Mock
from typing import List, Dict
from tests.test_helpers import test_db
from src.repositories.game_repository import *
# Importa la función que deseas probar
# from tu_modulo import list_lobbies

def test_list_lobbies(test_db):
    # Crear un mock para la base de datos    
    # Crear datos simulados de partidas

    # Partida 1: partida no iniciada, sin contraseña, 2 jugadores
    partida1 = Partida(game_name="partida1", max_players=4, password = None, partida_iniciada=False)

    # Partida 2: partida no iniciada, con contraseña, 3 jugadores
    partida2 = Partida(game_name="partida2", max_players=3, password = "U2FsdGVkX19Rw2m4lWQF8GsXaRT9h/OOM7e2MK8tKyE=", partida_iniciada=False)

    # Partida 3: partida iniciada
    partida3 = Partida(game_name="partida3", max_players=4, password = None, partida_iniciada=True)

    # Partida 4: partida no iniciada, sin contraseña, 0 jugadores
    partida4 = Partida(game_name="partida4", max_players=4, password = None, partida_iniciada=False)
    

    test_db.add(partida1)
    test_db.add(partida2)
    test_db.add(partida3)
    test_db.add(partida4)
    test_db.commit()

    # Jugadores de la partida 1
    jugador1 = Jugador(nombre="jugador1", partida_id=partida1.id, turno=0)
    jugador2 = Jugador(nombre="jugador2", partida_id=partida1.id, turno=1)
    test_db.add(jugador1)
    test_db.add(jugador2)

    # Jugadores de la partida 2
    jugador3 = Jugador(nombre="jugador3", partida_id=partida2.id, turno=0)
    jugador4 = Jugador(nombre="jugador4", partida_id=partida2.id, turno=1)
    jugador5 = Jugador(nombre="jugador5", partida_id=partida2.id, turno=2)
    test_db.add(jugador3)
    test_db.add(jugador4)
    test_db.add(jugador5)

    # Jugadores de la partida 3
    jugador6 = Jugador(nombre="jugador6", partida_id=partida3.id, turno=0)
    jugador7 = Jugador(nombre="jugador7", partida_id=partida3.id, turno=1)
    jugador8 = Jugador(nombre="jugador8", partida_id=partida3.id, turno=2)
    jugador9 = Jugador(nombre="jugador9", partida_id=partida3.id, turno=3)
    test_db.add(jugador6)
    test_db.add(jugador7)
    test_db.add(jugador8)
    test_db.add(jugador9)

    test_db.commit()
    
    # Ejecutar la función a probar
    result = list_lobbies(test_db)
    
    # Comprobar el resultado
    # La partida 3 no se veria por ser una partida iniciada, la partida 4 no se veria por no tener jugadores
    expected_result = [
        {
            "game_id": 1,
            "game_name": "partida1",
            "current_players": 2,
            "max_players": 4,
            "isPrivate": False
        },
        {
            "game_id": 2,
            "game_name": "partida2",
            "current_players": 3,
            "max_players": 3,
            "isPrivate": True
        }
    ]
    
    assert result == expected_result
