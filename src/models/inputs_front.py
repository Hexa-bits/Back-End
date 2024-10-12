from typing import Optional
from pydantic import BaseModel, Field

class Partida_config(BaseModel):
    id_user: int = Field (..., gt=0)
    game_name: str = Field (..., max_length=10)
    max_players: int = Field (..., gt=1, lt=5)

class Leave_config(BaseModel):
    id_user: int = Field (..., gt=0)
    game_id: int = Field (..., gt=0)

class PlayerId(BaseModel):
    player_id: int = Field (..., gt=0)

class User(BaseModel):
    username: str = Field (..., max_length=10)

class GameId(BaseModel):
    game_id: int = Field (..., gt=0)

class PlayerAndGameId(BaseModel):
    game_id: int = Field (..., gt=0)
    player_id: int = Field (..., gt=0)

class Coords(BaseModel):
    x: int = Field (..., gt=0, lt=37)
    y: int = Field (..., gt=0, lt=37)