from sqlalchemy import Column, String, Integer, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from src.db import Base


class Partida(Base):
    """
    Entidad que representa la partida. Posee un id unico, un nombre no nulo de hasta 10
    caracteres, un numero max de jugadores no nulo, un identificar de jugador en turno
    (utiliza el id de los jugadores en la partida) y un indicador de si la partida esta 
    inciada (en false quiere indicar que esta en lobby). Guarda relación muchos a uno
    con jugador, carta figura y carta movimiento, y relacion uno a uno con tablero. 
    """
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_name = Column(String(10), nullable=False)
    max_players = Column(Integer, nullable=False)
    jugador_en_turno = Column(Integer, default=0)
    partida_iniciada = Column(Boolean, default=False)

    jugadores = relationship("Jugador", back_populates="partida")

    cartafigura = relationship("PictureCard", back_populates="partida")
    tablero = relationship("Tablero", back_populates="partida", uselist=False)

    cartasmovimiento = relationship("MovementCard", back_populates="partida")

    def __repr__(self) -> str:
        id = f'id={self.id!r}'
        nombre = f'nombre={self.game_name!r}'
        cantidad_jugadores = f'cantidad_max_jugadores={self.max_players!r}'
        jugador_en_turno = f'jugador_en_turno={self.jugador_en_turno!r}'
        partida_iniciada = f'partida_iniciada={self.partida_iniciada}'
        return '{' + id + ', ' + nombre + ', ' + cantidad_jugadores + ', ' + jugador_en_turno + ', ' + partida_iniciada + '}'
