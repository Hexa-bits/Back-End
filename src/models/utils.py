from typing import Optional
from pydantic import BaseModel, Field

class Partida_config(BaseModel):
    """
    Se usa cómo configuración de partida. id_user es el id del jugador que inicia la partida
    (el owner) y debe ser un entero mayor a 0, game_name es el nombre del la partida y debe
    ser menor cómo max 10 carácteres, y max_players es un entero que debe estar entre 2 y 4. 
    """
    id_user: int = Field (..., gt=0)
    game_name: str = Field (..., max_length=10)
    max_players: int = Field (..., gt=1, lt=5)

class Leave_config(BaseModel):
    """
    Se usa para representar la data de la salida de un jugador, ya sea en una partida empezada
    o no empezada. id_user y game_id deben ser enteros mayores a 0.
    """
    id_user: int = Field (..., gt=0)
    game_id: int = Field (..., gt=0)

class PlayerId(BaseModel):
    """
    Se usa para representar el id del jugador, debe ser un entero mayor a 0.
    """
    player_id: int = Field (..., gt=0)

class User(BaseModel):
    """
    Se usa para representar el nombre del usuario al logearse, debe ser cómo max 10 caracteres
    """
    username: str = Field (..., max_length=10)

class GameId(BaseModel):
    """
    Se usa para representar el id de la partida, debe ser un entero mayor a 0.    
    """
    game_id: int = Field (..., gt=0)

class PlayerAndGameId(BaseModel):
    """
    Se usa para representar el id de la partida y el jugador, deben ser enteros mayores a 0 
    """
    game_id: int = Field (..., gt=0)
    player_id: int = Field (..., gt=0)


class Coords(BaseModel):
    """
    Se usa para presentar las coordenas del tablero, las coordenas deben ser enteros entre
    1 y 36.
    """
    x_pos: int = Field (..., gt=0, lt=37)
    y_pos: int = Field (..., gt=0, lt=37)
    
class MovementData(BaseModel):
    player_id: int = Field (..., gt=0)
    id_mov_card: int = Field (..., gt=0)
    fichas: tuple[Coords, Coords]