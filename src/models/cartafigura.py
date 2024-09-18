from sqlalchemy import Column, Enum, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from src.db import Base
import enum

pictures = [f'figura{i}' for i in range(1, 25)]

class Picture(enum.Enum):
    locals().update({name: enum.auto() for name in pictures})

class State(enum.Enum):
    mano: 1
    mazo: 2
    bloqueada: 3

class pictureCard(Base):
    __tablename__ = "cartasFigura"

    id = Column(Integer, primary_key=True, autoincrement=True)
    figura = Column(Enum(Picture))
    estado = Column(Enum(State))

    #partida_id = Column(Integer, ForeignKey("partidas.id"))
    #partida = relationship("Partida", back_populates="cartafigura")

    def __repr__(self) -> str:
        id = f'{self.id!r}'
        figura = f'{self.figura!r}'
        estado = f'{self.estado!r}'
        return 'id' + id + ', ' + figura + ', ' + estado