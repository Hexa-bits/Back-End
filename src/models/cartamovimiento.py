from sqlalchemy import Column, Enum, Integer, Boolean,ForeignKey
from sqlalchemy.orm import relationship
from src.db import Base
from src.models.jugadores import Jugador
import enum


class Move(enum.Enum):
    linea_contiguo = 1
    linea_con_espacio = 2
    diagonal_contiguo = 3
    diagonal_con_espacio = 4
    L_derecha = 5
    L_izquierda = 6
    linea_al_lateral = 7 # Ver si existe 

class CardStateMov(enum.Enum):
    mano = 1
    mazo = 2
    descartada = 3

class MovementCard(Base):
    __tablename__ = "cartasMovimiento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movimiento = Column(Enum(Move))
    estado = Column(Enum(CardStateMov), default=CardStateMov.mazo)

    partida_id = Column(Integer, ForeignKey("partidas.id"))
    partida = relationship("Partida", back_populates="cartasmovimiento")

    jugador_id = Column(Integer, ForeignKey("jugador.id"))
    jugador = relationship("Jugador", back_populates="cartasMovimiento" )
    
    def __repr__(self) -> str:
        id = f'{self.id!r}'
        movimiento = f'{self.movimiento!r}'
        estado = f'{self.estado!r}'
        return '{id' + id + ', ' + movimiento + ', ' + estado + '}'