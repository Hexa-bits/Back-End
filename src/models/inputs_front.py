from typing import Optional
from pydantic import BaseModel, conint, constr 

class Partida_config(BaseModel):
    id_user: int
    game_name: constr(max_length=10)
    max_players: conint(gt=1, lt=5)

class Leave_config(BaseModel):
    id_user: conint(gt=0)
    game_id: conint(gt=0)