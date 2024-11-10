from fastapi import status, HTTPException

from sqlalchemy.orm import Session

from src.models.utils import *

from src.repositories.board_repository import *
from src.repositories.game_repository import *
from src.repositories.player_repository import *
from src.repositories.cards_repository import *
from src.game_helpers import *

def validation_game(game_id: int, db: Session) -> Partida:
    """validación para asegurar existencia de partida"""
    game = get_Partida(game_id, db)
    if game is None or not game.partida_iniciada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'No existe la partida: {game_id}')
    return game

def validation_player(player_id: int, db: Session) -> Jugador:
    """validación para asegurar existencia de jugador"""
    player = get_Jugador(player_id, db)
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'No existe el jugador: {player_id}')
    return player

def validation_player_and_game(player_id: int, game_id: int, db: Session) -> Tuple[Jugador, Partida]:
    """validación para asegurar partida y jugador"""
    try:
        player = validation_player(player_id, db)
        game = validation_game(game_id, db)
        if player.partida_id == None or player.partida_id != game.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f'No exsite la partida asociada a jugador: {player.id}')

    except Exception as e:
        raise e
    return player, game

def validation_game_turn(player_id: int, game_id: int, db: Session) -> Tuple[Jugador, Partida]:
    """validación para asegurar jugador en turno"""
    try:
        player, game = validation_player_and_game(player_id, game_id, db)
        if player.turno != game.jugador_en_turno:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'No es el turno del jugador: {player.turno}, es de: {game.jugador_en_turno}')

    except Exception as e:
        raise e
    return player, game

def validation_game_fig_card(player_id: int, game_id: int, fig_id: int, db: Session) -> PictureCard:
    """validacion para carta de figura"""
    try:
        pictureCard = get_CartaFigura(fig_id, db)    
        
        if game_id != pictureCard.partida_id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no pertenece a la partida")
        
        if pictureCard.estado != CardState.mano:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no está en mano")
        
        if pictureCard.jugador_id != player_id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no pertenece al jugador")
    except Exception as e:
        raise e
    return pictureCard

def validation_leave(player_id: int, game_id: int, db: Session) -> Tuple[Jugador, Partida]:
    """validación para abandonar partida"""
    return validation_player_and_game(player_id, game_id, db)

def validation_join_game(game_id: int, db: Session) -> Partida:
    """validación para unirse a partida"""
    return validation_game(game_id, db)

def validation_get_winner(game_id: int, db: Session) -> Tuple[Jugador, Partida]:
    """validación para ganar partida"""
    return validation_game(game_id, db)

def validation_cancel_mov(player_id: int, game_id: int, db: Session) -> Tuple[Jugador, Partida]:
    """validación para cancelar movimiento"""
    return validation_game_turn(player_id, game_id, db)

def validation_use_fig_card(player_id: int, game_id: int, fig_id: int, db: Session) -> Tuple[Jugador, Partida, PictureCard]:
    """validación para usar carta figura"""
    try:
        player, game = validation_player_and_game(player_id, game_id, db)
        picture_card = validation_game_fig_card(player_id, game_id, fig_id, db)

    except Exception as e:
        raise e
    return player, game, picture_card 