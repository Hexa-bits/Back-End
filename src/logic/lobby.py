from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.models.partida import Partida
from src.models.jugadores import Jugador

def list_lobbies(db):

    raw_lobbies = db.query(Partida).all()
    
    lobbies = []
    print("Obteniendo lobbies...")

    print(raw_lobbies)

    for lobby in raw_lobbies:
        #Calculo la cantidad de jugadores actuales en partida
        current_players = db.query(Jugador).filter(Jugador.partida_id == lobby.id).count()

        lobbies.append({
            "game_id": lobby.id,
            "game_name": lobby.nombre,
            "current_players": current_players,
            "max_players": lobby.cantidad_max_jugadores,
            })

    return lobbies