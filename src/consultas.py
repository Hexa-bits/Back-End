from src.models.partida import Partida
from src.models.inputs_front import Partida_config
from src.models.jugadores import Jugador
from src.db import Session

from sqlalchemy import select

def get_Jugador(id: int) -> Jugador:
    with Session() as session:      
        smt = select(Jugador).where(Jugador.id == id)
        jugador = session.excecute(smt).scalar()
        return jugador
    
def jugador_anfitrion(id: int):
    jugador = get_Jugador(id)
    jugador.es_anfitrion = True
    with Session() as session:
        session.commit()

def add_partida(config: Partida_config) -> int:
    with Session() as session:
        partida = Partida(game_name=config.game_name, max_players=config.max_players)
        session.add(partida)
        session.commit()
        session.refresh(partida)
        return partida.id