from sqlalchemy.orm import Session
from src.models.partida import Partida
from src.models.inputs_front import Partida_config
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard
from src.models.tablero import Tablero
from src.models.cartamovimiento import MovementCard
from sqlalchemy import select
import random

def add_player(nombre: str, anfitrion: bool, db: Session) -> Jugador:
    jugador = Jugador(nombre= nombre, es_anfitrion= anfitrion)
    db.add(jugador)
    db.commit()  
    db.refresh(jugador)
    return jugador

def add_player_game(player_id: int, game_id: int, db: Session) -> Jugador:
    jugador = get_Jugador(player_id, db)
    jugador.partida_id = game_id
    db.commit()
    db.refresh(jugador)
    return jugador

def get_Jugador(id: int, db: Session) -> Jugador:
    smt = select(Jugador).where(Jugador.id == id)
    jugador = db.execute(smt).scalar()
    return jugador

def get_partida(id: int, db: Session) -> Partida:
    return db.query(Partida).filter(Partida.id==id).first()

def add_partida(config: Partida_config, db: Session) -> int:
    partida = Partida(game_name=config.game_name, max_players=config.max_players)
    jugador = get_Jugador(config.id_user, db)
    db.add(partida)
    db.commit()
    db.refresh(partida)
    jugador.es_anfitrion = True
    jugador.partida_id = partida.id
    db.commit()
    return partida.id

def list_lobbies(db):

    raw_lobbies = db.query(Partida).all()
    
    lobbies = []

    for lobby in raw_lobbies:
        #Calculo la cantidad de jugadores actuales en partida
        current_players = db.query(Jugador).filter(Jugador.partida_id == lobby.id).count()

        lobbies.append({
            "game_id": lobby.id,
            "game_name": lobby.game_name,
            "current_players": current_players,
            "max_players": lobby.max_players,
            })
        
    return lobbies

def mezclar_cartas_movimiento(db: Session, game_id: int):
    
    cards_mov_type = [1,2,3,4,5,6,7]
    
    for card_type in cards_mov_type:
        for i in range (7):
            #Añado la carta en la db
            carta_mov = MovementCard(movimiento=card_type, partida_id=game_id )
            db.add(carta_mov)
            db.commit()
            db.refresh(carta_mov)
            
    #Obtengo 3 cartas para cada jugador
    
    
    #random.shuffle(all_cards_mov)
    
    return
