from sqlalchemy.orm import Session
from src.models.partida import Partida
from src.models.inputs_front import Partida_config
from src.models.jugadores import Jugador
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from sqlalchemy import select, func, and_
import random
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
import random
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
import random
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


def get_Partida(id: int, db: Session) -> Partida:
    smt = select(Partida).where(Partida.id == id)
    partida = db.execute(smt).scalar()
    return partida


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


def delete_player(jugador: Jugador, db: Session):
    partida = get_Partida(jugador.partida_id, db)
    cant = player_in_partida(partida, db)
    if (partida.partida_iniciada and cant <= 2):
        delete_players_partida(partida, db)
    else: 
        jugador.partida_id = None
        db.commit()


def delete_partida(partida: Partida, db: Session):
    db.delete(partida)
    db.commit()


def delete_players_partida(partida: Partida, db: Session):
    smt = select(Jugador).where(Jugador.partida_id == partida.id)
    jugadores = db.execute(smt).scalars().all()
    for jugador in jugadores:
        jugador.partida_id = None
    db.commit()
    delete_partida(partida, db)


def player_in_partida(partida: Partida, db: Session) -> int:
    smt = select(func.count()).select_from(Jugador).where(Jugador.partida_id == partida.id)
    return db.execute(smt).scalar()


def list_lobbies(db):

    raw_lobbies = db.query(Partida).all()
    
    lobbies = []

    for lobby in raw_lobbies:
        #Calculo la cantidad de jugadores actuales en partida
        current_players = db.query(Jugador).filter(Jugador.partida_id == lobby.id).count()
        if current_players == 0 or lobby.partida_iniciada:
            continue
        lobbies.append({
            "game_id": lobby.id,
            "game_name": lobby.game_name,
            "current_players": current_players,
            "max_players": lobby.max_players,
            })
        
    return lobbies

def asignar_turnos(game_id: int, db: Session):
    player_list = get_jugadores(game_id, db)           #db.query(Jugador).filter(Jugador.partida_id == game_id).all()

    turnos = random.sample(range(len(player_list)), len(player_list))

    for jugador, turno in zip(player_list, turnos):
        jugador.turno = turno
        db.commit()
        db.refresh(jugador)

def get_jugadores(game_id: int, db: Session):
    return db.query(Jugador).filter(Jugador.partida_id == game_id).all()

def get_ordenes(id_game: int, db: Session) -> List[Jugador]:
    smt = select(Jugador).where(Jugador.partida_id == id_game)
    jugadores = db.execute(smt).scalars().all()
    jugadores.sort(key=lambda jugador: jugador.turno)
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
    try:
        partida = db.query(Partida).filter(Partida.id == game_id).first()
        jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).order_by(Jugador.turno).all()

    except Exception:
        raise Exception("Error")
    
    #hago una lista con los indices de los jugadores
    lista_turnos = [x.turno for x in jugadores]

    turno = partida.jugador_en_turno

    #Busco que lugar de la lista esta el jugador en turno
    index = lista_turnos.index(turno)

    #Si index falla porque el jugador en turno abandono partida, busco el numero siguiente
    # ESTO SERIA EN CASO QUE AL ABANDONAR NO SE PASARA EL TURNO
    # PERO NUESTRO ABANDONAR TURNO SI LLAMA A ESTE TERMINAR TURNO SI EL JUGADOR QUE ABANDONA ERA EL JUGADOR EN TURNO
    # es decir: SI JUGADOR_QUE_ABANDONA.TURNO == PARTIDA.JUGADOR_EN_TURNO deberia llamarse esta funcion

    #if index == -1:
    #    lista_turnos.append(turno)
    #    lista_turnos.sort()
    #    index = lista_turnos.index(turno)

    #indice del proximo jugador
    new_index = index + 1
    #Si me paso del final de la lista tomo  el primer jugador de nuevo
    if new_index == len(jugadores):
        new_index = 0
        
    partida.jugador_en_turno = lista_turnos[new_index]
    db.commit()
    
    json_jugador_turno = {
        "id_player": jugadores[new_index].id ,
        "name_player": jugadores[new_index].nombre
    }
    
    #Debo retornar lo que esta en la API formato JSON
    return json_jugador_turno

def mezclar_cartas_movimiento(db: Session, game_id: int):
    #Creo las cartas de movimiento
    cards_mov_type = [Move.linea_contiguo,Move.linea_con_espacio,
                    Move.diagonal_contiguo,Move.diagonal_con_espacio,
                    Move.L_derecha,Move.L_izquierda,Move.linea_al_lateral]
    
    for card_type in cards_mov_type:
        for i in range (7):
            #Añado la carta en la db
            carta_mov = MovementCard(movimiento=card_type, partida_id=game_id )
            db.add(carta_mov)
            db.commit()
            db.refresh(carta_mov)
    
    all_cards_mov = db.query(MovementCard).filter(MovementCard.partida_id == game_id).all()
    
    #Mezclo las cartas
    random.shuffle(all_cards_mov)
        
    #Obtengo 3 cartas para cada jugador
    #Obtengo mi lista de jugadores
    jugadores = db.query(Jugador).filter(Jugador.partida_id == game_id).all()
    
    for jugador in jugadores:
        for i in range(3):
            #Obtengo una carta aleatoria de all_cards_mov
            carta = all_cards_mov.pop()
            carta.jugador_id = jugador.id
            carta.estado = CardStateMov.mano
            db.commit()
            db.refresh(carta)
    return

def get_fichas(game_id: int, db: Session):

    tablero = db.query(Tablero).filter(Tablero.partida_id == game_id).first()

    all_fichas = db.query(FichaCajon).filter(FichaCajon.tablero_id == tablero.id).all()

    lista_fichas = []
    for ficha in all_fichas:
        #armo un json con las fichas
        lista_fichas.append({
            "x": ficha.x_pos,
            "y": ficha.y_pos,
            "color": ficha.color
        })
    response = { "fichas": lista_fichas }
    
    return response

def list_mov_cards(player_id: int, db: Session) -> List[int]:
    smt = select(MovementCard.movimiento).where(and_(MovementCard.jugador_id == player_id, MovementCard.estado == CardStateMov.mano))
    cards = db.execute(smt).scalars().all()
    res = []
    for card in cards:
        res.append(card.value)
    return res 

def list_fig_cards(player_id: int, db: Session) -> List[int]:
    smt = select(PictureCard.figura).where(and_(PictureCard.jugador_id == player_id, PictureCard.estado == CardState.mano))
    cards = db.execute(smt).scalars().all()
    res = []
    for card in cards:
        res.append(card.value)
    return res 