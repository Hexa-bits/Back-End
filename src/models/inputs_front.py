from typing import Optional, List
from pydantic import BaseModel, conint, constr 

class Partida_config(BaseModel):
    id_user: int
    game_name: constr(max_length=10)
    max_players: conint(gt=1, lt=5)

class Leave_config(BaseModel):
    id_user: conint(gt=0)
    game_id: conint(gt=0)

class PlayerId(BaseModel):
    id: int

class User(BaseModel):
    username: str

class GameId(BaseModel):
    game_id: int

class PlayerAndGameId(BaseModel):
    game_id: int
    player_id: int

class Ficha(BaseModel):
    x_pos: int
    y_pos: int
class MovementData(BaseModel):
    player_id: int
    id_mov_card: int
    fichas: List[Ficha]
class FigureData(BaseModel):
    player_id: int
    id_fig_card: int
    figura: List[Ficha]