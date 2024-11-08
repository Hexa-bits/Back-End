import asyncio
from fastapi import Depends, status, HTTPException, APIRouter
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError
from src.db import get_db
from sqlalchemy.orm import Session

from src.models.utils import *
from src.ws_manager import WebSocketConnectionManager

from src.repositories.board_repository import *
from src.repositories.game_repository import *
from src.repositories.player_repository import *
from src.repositories.cards_repository import *
from src.game_helpers import *
from src.models.patrones_figuras_matriz import generate_all_figures

router = APIRouter()

ws_manager = WebSocketConnectionManager()
game_manager = GameManager()

list_patterns = generate_all_figures()
list_patterns = [np.array(patron) for patron in list_patterns]

active_timers = {}

async def timer(game_id: int, db: Session):

    await asyncio.sleep(30)

    #-------
    player = get_current_turn_player(game_id, db)
        
    while game_manager.is_board_parcial(game_id):
        mov_coords = game_manager.top_tuple_card_and_box_cards(game_id)
        mov = mov_coords [0]
        coords = (mov_coords [1][0], mov_coords [1][1])

        cancel_movement(game_id, player.id, mov, coords, db)
        game_manager.pop_card_and_box_card(game_id)

    repartir_cartas(game_id, db)
    next_player = terminar_turno(game_id, db)
    game_manager.set_player_in_turn_id(game_id=game_id, jugador_id=next_player["id_player"])
       
    await ws_manager.send_end_turn(game_id)
    await timer_handler(game_id, db) 
    #--------  esto es lo mismo que en el endpoint end-turn, hay que modularizarlo a services o a otro lado

async def timer_handler(game_id: int, db: Session):
    if game_id in active_timers and not active_timers[game_id].done():
        active_timers[game_id].cancel()    
    active_timers[game_id] = asyncio.create_task(timer(game_id, db))


@router.websocket("")
async def websocket_endpoint(game_id: int, websocket: WebSocket):
    """
    Le permite al front escucha los mensajes entrantes, que se envían a
    todos aquellos en juego, ya sea lobby o en partida inciada por game_id
    """
    await ws_manager.connect(game_id=game_id, websocket=websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        await ws_manager.send_all_message("Un usuario se ha desconectado")

@router.put("/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_lobby(leave_lobby: Leave_config, db: Session=Depends(get_db)):
    """
    Descripción: Maneja la logica de abandonar partida, ya sea empezada (game) o no
    (lobby), borra las cartas figuras y devuelve las de movimiento al mazo, el último
    elimina la partida y con ello todas las carta, tablero y fihcas cajon.
    
    Respuesta:
    - 204: OK sin contenido
    - 404: No encontro partida, jugador o jugador asociado a partida
    - 500: Ocurre un error interno 
    """
    try:
        jugador = get_Jugador(leave_lobby.id_user, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No existe el jugador: {leave_lobby.id_user}')
        
        partida = get_Partida(leave_lobby.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f'No exsite la partida: {leave_lobby.game_id}')
        
        if jugador.partida_id == None or jugador.partida_id != partida.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f'No exsite la partida asociada a jugador: {leave_lobby.id_user}')

        game_id = partida.id
        if partida.partida_iniciada:
            is_current_turn_player = delete_player(jugador, db)
            await ws_manager.send_get_info_players(partida.id)
            if get_Partida(game_id, db) is None and not active_timers[game_id].done():
                if active_timers[game_id].cancel():
                    del active_timers[game_id]
            elif is_current_turn_player:
                await timer_handler(game_id, db)
            jugadores = get_players(game_id, db)
            
            if partida.winner_id is None and len(jugadores) == 1:
                partida.winner_id = jugadores[0].id
                db.commit()

                await ws_manager.send_get_winner(partida.id)
        else:
            if jugador.es_anfitrion:
                delete_players_lobby(partida, db)
                await ws_manager.send_cancel_lobby(game_id)
            else:
                delete_player(jugador, db)
                await ws_manager.send_leave_lobby(game_id)
        
            await ws_manager.send_get_lobbies()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail="Fallo en la base de datos")
    
@router.post("/join", response_model=PlayerAndGameId, status_code=status.HTTP_200_OK)
async def join_game(playerAndGameId: PlayerAndGameId, db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de unirse a una partida.

    Respuesta:
    - 200: OK.
    - 404: No existe la partida a la que se quiere unir o no existe el jugador.
    - 400: La partida ya esta empezada.
    - 500: Ocurre un error interno.
    """
    try:
        partida = get_Partida(playerAndGameId.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La partida no existe")
        
        if partida.partida_iniciada:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La partida ya esta empezada")

        jugador = add_player_game(playerAndGameId.player_id, playerAndGameId.game_id, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El jugador no existe")
        
        #Luego de unirse a la partida, le actualizo a los ws conectados la nueva lista de lobbies
        #Porque ahora tiene un jugador mas
        await ws_manager.send_get_lobbies()
        await ws_manager.send_join_game(partida.id)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al unirse a partida")
    return PlayerAndGameId(player_id=jugador.id, game_id=jugador.partida_id)


@router.get("/board", status_code=status.HTTP_200_OK)
async def get_board(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de pedir al servidor el tablero.

    Respuesta:
    - 200: OK.
    - 500: Ocurre un erro interno.
    """
    try:
        tablero = get_box_cards(game_id.game_id, db)
        is_parcial = game_manager.is_board_parcial(game_id.game_id)

        response = { "fichas": tablero,
                    "parcial": is_parcial }

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el tablero")
    return response


@router.put("/end-turn", status_code=status.HTTP_200_OK)
async def end_turn(game_id: GameId, db: Session = Depends(get_db)):
    """
    Descripción: Endpoint que maneja la lógica de pasar el turno. Recibe el id del juego
    del cual se pasa el turno.

    Respuesta:
    - 200: Diccionario con el jugador del turno siguiente.
    - 500: En caso de algún fallo en base de datos. Con contenido "Fallo en la base de datos"
    """
    try:
        jugador = get_current_turn_player(game_id.game_id, db)
        
        while game_manager.is_board_parcial(game_id.game_id):
            mov_coords = game_manager.top_tuple_card_and_box_cards(game_id.game_id)
            mov = mov_coords [0]
            coords = (mov_coords [1][0], mov_coords [1][1])

            cancel_movement(game_id.game_id, jugador.id, mov, coords, db)
            game_manager.pop_card_and_box_card(game_id.game_id)
        
        repartir_cartas(game_id.game_id, db)
        next_jugador = terminar_turno(game_id.game_id, db)
        #TO DO: ver si quitar jugador en turno de game_manager
        game_manager.set_player_in_turn_id(game_id=game_id.game_id, player_id=next_jugador["id_player"])
       
        await ws_manager.send_end_turn(game_id.game_id)
        await timer_handler(game_id.game_id, db) 
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al finalizar el turno")
    return next_jugador


@router.get("/my-fig-card/", status_code=status.HTTP_200_OK)
async def get_fig_card(player_id: PlayerId = Depends(), db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de pedir al servidor las cartas de figura
    en mano de un jugador.

    Respuesta:
    - 200: OK.
    - 500: Ocurre un error interno.
    """
    try:
        fig_cards = list_fig_cards(player_id.player_id, db)
        fig_cards_list = []
        for card in fig_cards:
            fig_cards_list.append({"id": card.id, "fig": card.figura.value})
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(    
        content={"fig_cards": fig_cards_list},
        status_code=status.HTTP_200_OK
    )


@router.get("/my-mov-card", status_code=status.HTTP_200_OK)
async def get_mov_card(player_id: PlayerId = Depends(), db: Session = Depends(get_db)):
    """
    Descripción: manejo la logica de pedir al servidor la cartas de movimiento
    en mano de un jugador.

    Respuesta:
    - 200: OK.
    - 500: Ocurre un erro interno.
    """
    try:
        mov_cards = list_mov_cards(player_id.player_id, db)
        mov_cards_list = []
        for card in mov_cards:
            mov_cards_list.append({"id": card.id, "move": card.movimiento.value})
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content={"mov_cards": mov_cards_list},
        status_code=status.HTTP_200_OK
    )


@router.get("/get-winner", status_code=status.HTTP_200_OK)
async def get_winner(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    """
    Descripción: Maneja la logica de decidir ganador en partida.

    Respuesta:
    - 200: OK con nombre de jugador que ganó.
    - 400: Si se llama, pero no hubo ganador de ningun metodo.
    - 404: Si la partida no existe.
    - 500: Ocurre un error interno. 
    """
    try:
        # A como estaba antes era demasiado inseguro, cualquiera de conociera el endpoint podía ganar automaticamente.
        partida = get_Partida(game_id.game_id, db)
        if partida is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"No existe la partida: {game_id.game_id}")
        
        winner_id = partida.winner_id
        winner = get_Jugador(winner_id, db)
        if winner is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail=f"No hay ganador aún en partida: {game_id.game_id}")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content= {"name_player": winner.nombre},
        status_code=status.HTTP_200_OK
    )
    

@router.get("/current-turn", status_code=status.HTTP_200_OK)
async def get_current_turn(game_id: GameId = Depends(), db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de pedir al servidor el jugador en turno de la partida.

    Respuesta:
    - 200: OK.
    - 500: Ocurre un error interno.
    """
    try:
        jugador = jugador_en_turno(game_id.game_id, db)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener el jugador actual en turno")
    return jugador


@router.put("/start-game", status_code= status.HTTP_200_OK)
async def start_game(game_id: GameId, db: Session = Depends(get_db)):
    """
    Descripción: maneja la logica de empezar una partida. Crea todas las instancias
    de tablero, cartas de movimientos, figuras y fichas cajon.

    Respuesta: 
    - 200: OK.
    - 500: Ocurre error interno.
    """
    try:
        partida = get_Partida(game_id.game_id, db)
        if not partida.partida_iniciada:
            mezclar_box_cards(db, game_id.game_id)
            mezclar_cartas_movimiento(db, game_id.game_id)
            mezclar_figuras(game_id.game_id, db)
            asignar_turnos(game_id.game_id, db)
            partida.partida_iniciada = True
            db.commit()
            #Envio la lista de partidas actualizadas a ws ya que se inicio una partida

            #Uso el game manager
            game_manager.create_game(game_id.game_id)
            
            await ws_manager.send_get_lobbies()
            await ws_manager.send_start_game(game_id.game_id)
            asyncio.create_task(timer_handler(game_id.game_id, db))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")
    return JSONResponse(
        content={"id_game": game_id.game_id, "iniciada": partida.partida_iniciada},
        status_code=status.HTTP_200_OK
    )


@router.put("/cancel-mov", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_mov(playerAndGameId: PlayerAndGameId, db: Session = Depends(get_db)):
    """
    Descripción: Maneja la lógica de cancelar movimiento.

    Respuesta:
    - 204: OK sin contenido en caso de que todo salga bien.
    - 400: Una request donde no hay movimientos que deshacer o
           no es el turno del jugador en cuestión.
    - 404: La partida, el juego o la relacione entre ambos no existe.
    - 500: Ocurre un error interno. 
    """
    try:
        jugador = get_Jugador(playerAndGameId.player_id, db)
        if jugador is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f'No existe el jugador: {playerAndGameId.player_id}')
        
        partida = get_Partida(playerAndGameId.game_id, db)
        if partida is None or not partida.partida_iniciada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f'No existe la partida: {playerAndGameId.game_id}')
        
        if jugador.partida_id == None or jugador.partida_id != partida.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'No existe la partida asociada a jugador: {playerAndGameId.player_id}')
        
        if jugador.turno != partida.jugador_en_turno:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'No es el turno del jugador: {jugador.turno}, es de: {partida.jugador_en_turno}')

        mov_coords = game_manager.top_tuple_card_and_box_cards(game_id=partida.id)
        if mov_coords is not None:
            mov = mov_coords [0]
            coords = (mov_coords [1][0], mov_coords [1][1])
            try:
                cancel_movement(partida.id, jugador.id, mov, coords, db)
                
                await ws_manager.send_get_tablero(partida.id)
                await ws_manager.send_get_cartas_mov(partida.id)

                game_manager.pop_card_and_box_card(game_id=partida.id) 
            except Exception:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Fallo en la base de datos")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No hay movimientos que deshacer')
        
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Fallo en la base de datos')

@router.put("/use-mov-card", status_code= status.HTTP_200_OK)
async def use_mov_card(movementData: MovementData, db: Session = Depends(get_db)):
    """
    Descripción: Este endpoint maneja la lógica de usar una carta de movimiento.

    Respuesta:
    - 200: Sin contenido en caso de que el movimiento sea válido.
    - 400: Una request incorrecta con contenido: 
            * "Movimiento invalido" en caso de que las fichas a swapear no coincidan
              con el movimiento.
            * "La carta no pertenece a la partida"
            * "No es turno del jugador"
            * "La carta no está en mano"
            * "La carta no pertenece al jugador" 
    - 500: En caso de algún fallo en base de datos. Con contenido "Fallo en la base de datos"
    
    Ejemplo de uso:
    PUT /game/use-mov-card, con body:
        {player_id: int
        id_mov_card: int
        fichas: [{x_pos: int, y_pos: int}]}
    """

    try:
        jugador = get_Jugador(movementData.player_id, db)
        movementCard = get_CartaMovimiento(movementData.id_mov_card, db)
        game_id = jugador.partida_id
        if game_id != movementCard.partida_id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no pertenece a la partida")
        
        jugador_en_turno = get_current_turn_player(game_id, db)
        if jugador_en_turno.id != jugador.id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="No es turno del jugador")
        
        if movementCard.estado != CardStateMov.mano:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no está en mano")
        
        if movementCard.jugador_id!=jugador.id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no pertenece al jugador")
        
        coord = (movementData.fichas[0], movementData.fichas[1])
        
        if is_valid_move(movementCard, coord):
            movimiento_parcial(game_id, movementCard, coord, db)
            game_manager.add_card_and_box_card(game_id, movementCard.id, coord)
            
            await ws_manager.send_get_tablero(game_id)
            await ws_manager.send_get_cartas_mov(game_id)
        else:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Movimiento invalido")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")  


@router.put("/use-fig-card", status_code= status.HTTP_200_OK)
async def use_fig_card(figureData: FigureData, db: Session = Depends(get_db)):
    """
    Descripción: Este endpoint maneja la lógica de descartarse una carta de figura.

    Respuesta:
    - 200: Sin contenido en caso de que el movimiento sea válido.
    - 400: Una request incorrecta con contenido: 
            * "Figura invalida" en caso de que la figura a matchear no coincida
              con la figura de la carta.
            * "La carta no pertenece a la partida"
            * "No es turno del jugador"
            * "La carta no está en mano"
            * "La carta no pertenece al jugador" 
    - 500: En caso de algún fallo en base de datos. Con contenido "Fallo en la base de datos"
    
    Ejemplo de uso:
    PUT /game/use-fig-card, con body:
        {player_id: int
        id_fig_card: int
        figura: [{x_pos: int, y_pos: int}]}
    """
    try:
        if (len(figureData.figura)==0):
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Figura invalida")
        
        jugador = get_Jugador(figureData.player_id, db)
        pictureCard = get_CartaFigura(figureData.id_fig_card, db)
        
        game_id = jugador.partida_id
        partida = get_Partida(game_id, db)
        
        if game_id != pictureCard.partida_id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no pertenece a la partida")
        
        id_jugador_en_turno = get_current_turn_player(game_id, db).id
        if id_jugador_en_turno!=jugador.id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="No es turno del jugador")
        
        if pictureCard.estado != CardState.mano:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no está en mano")
        
        if pictureCard.jugador_id != jugador.id:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="La carta no pertenece al jugador")
        
        if is_valid_picture_card(pictureCard, figureData.figura):
            descartar_carta_figura(pictureCard.id, db)
            game_manager.clean_cards_box_cards(game_id)

            if partida.winner_id is None and get_jugador_sin_cartas(game_id, db) is not None:
                partida.winner_id = jugador.id
                db.commit()

                await ws_manager.send_get_winner(game_id)
            else:
                await ws_manager.send_get_cartas_fig(game_id)
            await ws_manager.send_get_tablero(game_id)
        else:
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Figura invalida")     
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fallo en la base de datos")   


@router.get("/highlight-figures", status_code=status.HTTP_200_OK)
async def highlight_figures(game_id: int, db: Session = Depends(get_db)):
    """
    Endpoint para resaltar las figuras detectadas en el tablero
    args:
        game_id: int - id del juego
    return:
        list - Lista de figuras(cada figura es una lista de diccionarios) detectadas en el tablero
    """

    try:
        #Obtengo la lista de figuras(lista de coordenadas) detectadas como validas en el tablero
        figuras = get_valid_detected_figures(game_id, list_patterns, db)

        # Creo una lista para adaptarme al formato de respuesta
        figuras_response = []    
        for figura in figuras:
            list_dicc_fig = []  # Lista para almacenar los diccionarios de una figura
            for (x, y) in figura:
                # Convertir la tupla en un diccionario y agregarla a la nueva figura
                #Sumo 1 a x,y para que empiece en 1,1 como en el tablero
                list_dicc_fig.append({
                                    'x': x+1,
                                    'y': y+1,
                                    'color': get_color_of_box_card(x+1, y+1, game_id, db)
                                    })
                
            figuras_response.append(list_dicc_fig)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener las figuras")
    
    return figuras_response

@router.get("/others-cards", status_code=status.HTTP_200_OK)
async def get_others_cards(game_id: int, player_id : int, db: Session = Depends(get_db)):
    """
    Endpoint para obtener nombre, las cartas de figuras y cant de cartas movimiento de los demás jugadores
    args:
        game_id: int - id del juego
        player_id: int - id del jugador
    """

    try:
        #Obtengo los jugadores de la aprtida
        jugadores = get_players(game_id, db)
        # Obtengo las cartas de figuras y movimiento de los demás jugadores junto con el nombre del jugador
        cartas = others_cards(player_id, jugadores, db)

    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al obtener las cartas de los demás jugadores")
    
    return cartas