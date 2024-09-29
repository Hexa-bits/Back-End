from sqlalchemy.orm import Session
from src.models.partida import Partida
from src.models.inputs_front import Partida_config
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.cartamovimiento import MovementCard
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
import random
from sqlalchemy import select
from typing import List

def add_player(nombre: str, anfitrion: bool, db: Session) -> Jugador:
    jugador = Jugador(nombre= nombre, es_anfitrion= anfitrion)
    db.add(jugador)
    db.commit()  
    db.refresh(jugador)
    return jugador

def get_lobby(game_id: int, db: Session):
    try:
        partida = db.query(Partida).filter(Partida.id == game_id).first()
    except Exception:
        raise Exception("Error al obtener la partida")
    
    if partida is None:
        raise Exception("No existe la partida")
    
    lista_jugadores = []
    
    try:
    #List of players name order by es_anfitrion==True first
        jugadores_en_partida = db.query(Jugador).filter(Jugador.partida_id == game_id).order_by(Jugador.es_anfitrion.desc()).all()
        for jugador in jugadores_en_partida:
            lista_jugadores.append(jugador.nombre)
    except Exception:
        raise Exception("Error al obtener los jugadores de la partida")

    lobby_info = {
        "game_name": partida.game_name,
        "max_players": partida.max_players,
        "name_players": lista_jugadores
    }

    return lobby_info
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


def get_ordenes(id_game: int, db: Session) -> List[Jugador]:
    #Obtengo todos los jugadores de la partida en orden de turno ascendente
    jugadores = db.query(Jugador).filter(Jugador.partida_id == id_game).order_by(Jugador.turno).all()
    
    return jugadores


def get_CartaFigura(id_carta_figura: int, db: Session) -> PictureCard:
    smt = select(PictureCard).where(PictureCard.id == id_carta_figura)
    return db.execute(smt).scalar() 


def repartir_cartas_figuras (game_id: int, figuras_list: List[int], db: Session):
    jugadores = get_ordenes(game_id, db)
    num_jugadores = len(jugadores)

    cartas_total = (50 // num_jugadores) *num_jugadores

    for i in range(cartas_total):

        cartaFigura = PictureCard(figura=Picture(figuras_list[i]))
        if (i < 3 *num_jugadores):
            cartaFigura.estado = CardState.mano

        cartaFigura.partida_id = game_id
        cartaFigura.jugador_id = jugadores[i % num_jugadores].id
        i += num_jugadores
        db.add(cartaFigura)

    db.commit()


def get_cartasFigura_player(player_id: int, db: Session) -> List[PictureCard]:
    smt = select(PictureCard).where(PictureCard.jugador_id == player_id)
    return db.execute(smt).scalars().all()


def mezclar_fichas(db: Session, game_id: int):

    tablero = Tablero(partida_id=game_id)
    db.add(tablero)
    db.commit()
    db.refresh(tablero)

    #Creo una lista con las 36 coord
    coordenadas = []
    for i in range(1,7):
        for j in range(1,7):
            coordenadas.append((i,j))

    #Creo una lista con 9 veces repetido cada color del enum
    colores = [Color.ROJO]*9 + [Color.VERDE]*9 + [Color.AMARILLO]*9 + [Color.AZUL]*9

    #mezclo los colores que le corresponderia a cada casilla
    random.shuffle(colores)

    #Asigno cada color a una ficha cajon
    for coord in coordenadas:
        x, y = coord
        color = colores.pop()
        ficha = FichaCajon(x_pos=x, y_pos=y, color=color, tablero_id=tablero.id)
        db.add(ficha)
        db.commit()
        db.refresh(ficha)
    
    return tablero.id

def terminar_turno(game_id: int, db: Session):
    #Obtengo la partida
    #partida = get_partida(game_id, db)
    try:
        partida = db.query(Partida).filter(Partida.id == game_id).first()
        print(partida)

        pep = db.query(Jugador).filter(Jugador.partida_id == game_id).count()
        print(pep)

        jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).order_by(Jugador.turno).all()
        print(jugadores)

    except Exception:
        raise Exception("Error")
    
    #hago una lista con los indices de los jugadores
    lista_turnos = [x.turno for x in jugadores]
    print(lista_turnos)

    turno = partida.jugador_en_turno
    print(turno)

    #Busco que lugar de la lista esta el jugador en turno
    index = lista_turnos.index(turno)
    print(index)

    #Si index falla porque el jugador en turno abandono partida, busco el numero siguiente
    # ESTO SERIA EN CASO QUE AL ABANDONAR NO SE PASARA EL TURNO
    # PERO NUESTRO ABANDONAR TURNO SI LLAMA A ESTE TERMINAR TURNO SI EL JUGADOR QUE ABANDONA ERA EL JUGADOR EN TURNO
    # es decir: SI JUGADOR_QUE_ABANDONA.TURNO == PARTIDA.JUGADOR_EN_TURNO deberia llamarse esta funcion

    #if index == -1:
    #    lista_turnos.append(turno)
    #    lista_turnos.sort()
    #    index = lista_turnos.index(turno)
    #    print(index)

    #indice del proximo jugador
    new_index = index + 1
    #Si me paso del final de la lista tomo  el primer jugador de nuevo
    if new_index == len(jugadores):
        new_index = 0
        
    partida.jugador_en_turno = lista_turnos[new_index]
    print(partida.jugador_en_turno)
    db.commit()
    
    json_jugador_turno = {
        "id_player": jugadores[new_index].id ,
        "name_player": jugadores[new_index].nombre
    }
    
    #Debo retornar lo que esta en la API formato JSON
    return json_jugador_turno