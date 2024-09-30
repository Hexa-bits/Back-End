from fastapi import FastAPI, Request, Depends, status, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel

from sqlalchemy.exc import SQLAlchemyError
from src.db import Base, engine, SessionLocal, get_db
from sqlalchemy.orm import Session

from src.models.jugadores import Jugador
from src.models.partida import Partida
from src.models.inputs_front import Partida_config, Leave_config
from src.models.tablero import Tablero
from src.models.cartafigura import PictureCard
from src.models.cartamovimiento import MovementCard
from src.models.fichas_cajon import FichaCajon

from src.consultas import *

from sqlalchemy.exc import IntegrityError

import random


router = APIRouter()


class GameId(BaseModel):
    game_id: int

class PlayerAndGameId(BaseModel):
    game_id: int
    player_id: int


@router.put("/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_game(leave_game: Leave_config, db: Session=Depends(get_db)):
    try:
        jugador = get_Jugador(leave_game.id_user, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No existe el jugador: {leave_game.id_user}')
        
        partida = get_Partida(leave_game.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No exsite la partida: {leave_game.game_id}')
        
        if jugador.partida_id == None or jugador.partida_id != partida.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No exsite la partida asociada a jugador: {leave_game.id_user}')

        if partida.partida_iniciada:
            delete_player(jugador, db)
        else:
            if jugador.es_anfitrion:
                delete_players_partida(partida, db)
            else:
                delete_player(jugador, db)
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    
    
@router.post("/join", response_model=PlayerAndGameId, status_code=status.HTTP_200_OK)
async def join_game(playerAndGameId: PlayerAndGameId, db: Session = Depends(get_db)):
    try:
        partida = get_Partida(playerAndGameId.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La partida no existe")
        
        jugador = add_player_game(playerAndGameId.player_id, playerAndGameId.game_id, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El jugador no existe")
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al unirse a partida")
    return PlayerAndGameId(player_id=jugador.id, game_id=jugador.partida_id)


@router.get("/board", status_code=status.HTTP_200_OK)
async def get_board(game_id: int, db: Session = Depends(get_db)):
    try:
        tablero = get_fichas(game_id, db)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el tablero")
    return tablero


@router.put("/end-turn", status_code=status.HTTP_200_OK)
async def end_turn(game_id: GameId, db: Session = Depends(get_db)):
    try:
        next_jugador = terminar_turno(game_id.game_id, db)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al finalizar el turno")
    return next_jugador


def mezclar_figuras(game_id: int, db: Session = Depends(get_db)):
    figuras_list = [x for x in range(1, 26)] + [x for x in range(1, 26)]
    random.shuffle(figuras_list)
    repartir_cartas_figuras(game_id, figuras_list, db)


@router.get("/my-fig-card/", status_code=status.HTTP_200_OK)
async def get_mov_card(player_id: int, db: Session = Depends(get_db)):
    try:
        id_fig_cards = list_fig_cards(player_id, db)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(    
        content={"id_fig_card": id_fig_cards},
        status_code=status.HTTP_200_OK
    )


@router.get("/my-mov-card", status_code=status.HTTP_200_OK)
async def get_mov_card(player_id: int, db: Session = Depends(get_db)):
    try:
        id_mov_cards = list_mov_cards(player_id, db)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content={"id_mov_card": id_mov_cards},
        status_code=status.HTTP_200_OK
    )


@router.get("/get-winner", status_code=status.HTTP_200_OK)
async def get_winner(game_id: int, db: Session = Depends(get_db)):
    try:
        jugadores = get_jugadores(game_id, db)
        if len(jugadores)==1:
            winner = jugadores[0]
            return JSONResponse(
                content= {"id_player": winner.id, "name_player": winner.nombre}
            )
        else:
            raise HTTPException(status_code=204, detail="No hay un ganador")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    

@router.get("/current-turn", status_code=status.HTTP_200_OK)
async def get_current_turn(game_id: int, db: Session = Depends(get_db)):
    try:
        jugador = jugador_en_turno(game_id, db)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el jugador actual en turno")
    return jugador


@router.put("/start-game", status_code= status.HTTP_200_OK)
async def start_game(game_id: GameId, db: Session = Depends(get_db)):
    try:
        partida = get_Partida(game_id.game_id, db)
        if not partida.partida_iniciada:
            mezclar_fichas(db, game_id.game_id)
            mezclar_cartas_movimiento(db, game_id.game_id)
            mezclar_figuras(game_id.game_id, db)
            asignar_turnos(game_id.game_id, db)
            partida.partida_iniciada = True
            db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content={"id_game": game_id.game_id, "iniciada": partida.partida_iniciada},
        status_code=status.HTTP_200_OK
    )