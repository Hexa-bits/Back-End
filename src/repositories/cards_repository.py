import random
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from src.models.partida import Partida
from src.models.utils import Partida_config
from src.models.jugadores import Jugador
from src.models.utils import Coords
from src.models.cartafigura import PictureCard, CardState, Picture
from src.models.tablero import Tablero
from src.models.fichas_cajon import FichaCajon
from src.models.color_enum import Color
from src.models.cartamovimiento import MovementCard, Move, CardStateMov
from src.repositories.board_repository import swap_fichasCajon

def get_CartaFigura(id_carta_figura: int, db: Session) -> PictureCard:
    """
    Obtiene una carta de figura por su id
    """
    smt = select(PictureCard).where(PictureCard.id == id_carta_figura)
    return db.execute(smt).scalar() 

def get_CartaMovimiento(id_carta_movimiento: int, db: Session) -> MovementCard:
    smt = select(MovementCard).where(MovementCard.id == id_carta_movimiento)
    return db.execute(smt).scalar() 

def list_fig_cards(player_id: int, db: Session) -> List[PictureCard]:
    smt = select(PictureCard).where(and_(PictureCard.jugador_id == player_id, PictureCard.estado == CardState.mano))
    return db.execute(smt).scalars().all()
 
def list_mov_cards(player_id: int, db: Session) -> List[MovementCard]:
    """
    Lista el tipo de cartas de figura en mano de un jugador  
    """
    smt = select(MovementCard).where(and_(MovementCard.jugador_id == player_id, MovementCard.estado == CardStateMov.mano))
    return db.execute(smt).scalars().all()

def mezclar_figuras(game_id: int, db: Session) -> None:
    """
    Mezcla las cartas de figuras de una partida y las reparte entre los 
    jugadores de la partida.
    """
    figuras_list = [x for x in range(1, 26)] + [x for x in range(1, 26)]
    random.shuffle(figuras_list)
    # TO DO: remover repartir_cartas_figuras, nombre confuso y sólo se usa al mezclar las cartas
    repartir_cartas_figuras(game_id, figuras_list, db)

def mezclar_cartas_movimiento(db: Session, game_id: int) -> None:
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


def repartir_cartas(game_id: int, db: Session) -> None:
    partida = db.query(Partida).filter(Partida.id == game_id).first()

    turno_actual = partida.jugador_en_turno

    jugador_en_turno = db.query(Jugador).filter(and_(Jugador.partida_id == game_id, Jugador.turno == turno_actual)).first()

    cartas_mov_en_mano = db.query(MovementCard).filter(and_(MovementCard.jugador_id == jugador_en_turno.id, 
                                                        MovementCard.estado == CardStateMov.mano)).all()
    
    cartas_fig_en_mano = db.query(PictureCard).filter(and_(PictureCard.jugador_id == jugador_en_turno.id, 
                                                           PictureCard.estado == CardState.mano)).all()

    if len(cartas_mov_en_mano) < 3:
        
        all_cards_mov = db.query(MovementCard).filter(and_(MovementCard.partida_id == game_id,
                                                           MovementCard.estado == CardStateMov.mazo)).all()
        
        cant_cartas = 3 - len(cartas_mov_en_mano)

        for i in range(cant_cartas):
            
            if len(all_cards_mov) == 0:
                cartas_mov_descartadas = db.query(MovementCard).filter(and_(MovementCard.partida_id == game_id,
                                                            MovementCard.estado == CardStateMov.descartada)).all()
                for carta in cartas_mov_descartadas:
                    carta.estado = CardStateMov.mazo
                    all_cards_mov.append(carta)
                    db.commit()
                    db.refresh(carta)
                    
            carta = random.choice(all_cards_mov)
            all_cards_mov.remove(carta)
            carta.jugador_id = jugador_en_turno.id
            carta.estado = CardStateMov.mano
            db.commit()
            db.refresh(carta)
    
    if len(cartas_fig_en_mano) < 3:
        
        all_cards_fig_player = db.query(PictureCard).filter(and_(PictureCard.partida_id == game_id,
                                                          PictureCard.jugador_id == jugador_en_turno.id,
                                                          PictureCard.estado == CardState.mazo)).all()
        
        cant_cartas = 3 - len(cartas_fig_en_mano)

        for i in range(cant_cartas):
            if len(all_cards_fig_player)>0:
                carta = all_cards_fig_player.pop()
                carta.jugador_id = jugador_en_turno.id
                carta.estado = CardState.mano
                db.commit()
                db.refresh(carta)

def repartir_cartas_figuras (game_id: int, figuras_list: List[int], db: Session) -> None:
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

def descartar_carta_figura(id: int, db: Session) -> None:
    card = get_CartaFigura(id, db)
    card.partida_id = None
    card.jugador_id = None
    db.delete(card)
    db.commit()

def cards_to_mazo(partida: Partida, jugador: Jugador, db: Session) -> None:
    figs = get_cartasFigura_player(jugador.id, db)
    for fig in figs:
        fig.partida_id = None
        fig.jugador_id = None
        db.delete(fig)
    
    movs = get_cartasMovimiento_player(partida.id, db)
    for mov in movs:
        mov.jugador_id = None
        mov.estado = CardStateMov.mazo
    
    db.commit()


def get_cartasFigura_player(player_id: int, db: Session) -> List[PictureCard]:
    smt = select(PictureCard).where(PictureCard.jugador_id == player_id)
    return db.execute(smt).scalars().all()


def get_cartasMovimiento_player(player_id: int, db: Session) -> List[MovementCard]:
    smt = select(MovementCard).where(MovementCard.jugador_id == player_id)
    return db.execute(smt).scalars().all()


def get_cartasMovimiento_game(game_id: int, db: Session) -> List[MovementCard]:
    smt = select(MovementCard).where(MovementCard.partida_id == game_id)
    return db.execute(smt).scalars().all()


def get_ordenes(id_game: int, db: Session) -> List[Jugador]:
    smt = select(Jugador).where(Jugador.partida_id == id_game)
    jugadores = db.execute(smt).scalars().all()
    jugadores.sort(key=lambda jugador: jugador.turno)
    return jugadores

def others_cards(game_id: int, player_id: int, jugadores: List[Jugador], db: Session) -> List[dict]:


    jugadores_info = []
    for jugador in jugadores:
        if jugador.id != player_id:
            jugador_info = {}
            jugador_info["nombre"] = jugador.nombre

            cartas_figura = get_cartasFigura_player(jugador.id, db)
            cartas_mov = get_cartasMovimiento_player(jugador.id, db)

            jugador_info["fig_cards"] = []
            for carta in cartas_figura:
                #Solo quiero enviar las cartas figura visibles
                if carta.estado == CardState.mano:
                    carta_info = {}
                    carta_info["id"] = carta.id
                    carta_info["fig"] = carta.figura.value
                    jugador_info["fig_cards"].append(carta_info)
            
            jugador_info["mov_cant"] = len(cartas_mov)

            jugadores_info.append(jugador_info)
    return jugadores_info

def get_cartaMovId(mov_id: int, db: Session) -> MovementCard:
    """
    Obtiene una carta de movimiento por su id
    """
    smt = select(MovementCard).where(MovementCard.id == mov_id)
    return db.execute(smt).scalar()


def cancelar_movimiento(partida_id: int, jugador_id: int, mov_id: int,
                        tupla_coords: tuple[Coords, Coords], db: Session) -> None:
    """
    Cancela un movimiento revertiendo la posición de las fichasCajon usadas 
    (swap_fichasCajon), y devolviendo a la mano del jugador una carta de 
    movimiento usada.
    """
    #Hace que la operación sea atómica (si ocurre un error hace rollback de todo)
    swap_fichasCajon(partida_id, tupla_coords, db)        
    carta_mov = get_cartaMovId(mov_id, db)
    
    if carta_mov is None:
        raise ValueError("La carta de movimiento no existe en la partida")
    elif carta_mov.estado == CardStateMov.mano:
        raise ValueError("La carta de movimiento esta en mano de alguien")
    
    carta_mov.estado = CardStateMov.mano
    carta_mov.jugador_id = jugador_id
    
    db.commit()

def movimiento_parcial(game_id: int, moveCard: MovementCard, 
                       coord: tuple[Coords, Coords], db: Session) -> None:
    """
    Realiza movimiento en el tablero, intercambiando fichas cajon 
    (usa swap_fichasCajon), y llevando la carta de movimiento usada al estado
    de descartada.
    """
    swap_fichasCajon(game_id, coord, db)

    moveCard.estado = CardStateMov.descartada
    moveCard.jugador_id = None

    db.commit()
