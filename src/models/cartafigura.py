from sqlalchemy import Column, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.db import Base
import enum


class Picture(enum.Enum):
    figura1 = 1
    figura2 = 2
    figura3 = 3
    figura4 = 4
    figura5 = 5
    figura6 = 6
    figura7 = 7
    figura8 = 8
    figura9 = 9
    figura10 = 10
    figura11 = 11
    figura12 = 12
    figura13 = 13
    figura14 = 14
    figura15 = 15
    figura16 = 16
    figura17 = 17
    figura18 = 18
    figura19 = 19
    figura20 = 20
    figura21 = 21
    figura22 = 22
    figura23 = 23
    figura24 = 24
    figura25 = 25

class CardState(enum.Enum):
    mano = 1
    mazo = 2
    bloqueada = 3

class pictureCard(Base):
    __tablename__ = "cartasFigura"

    id = Column(Integer, primary_key=True, autoincrement=True)
    figura = Column(Enum(Picture))
    estado = Column(Enum(CardState))

    partida_id = Column(Integer, ForeignKey("partidas.id"))
    partida = relationship("Partida", back_populates="cartafigura")

    def __repr__(self) -> str:
        id = f'{self.id!r}'
        figura = f'{self.figura!r}'
        estado = f'{self.estado!r}'
        return 'id' + id + ', ' + figura + ', ' + estado