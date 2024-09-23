from src.models.color_enum import Color
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Enum
from src.db import Base
from src.models.tablero import Tablero

class FichaCajon(Base):
    __tablename__ = "fichas"

    id = Column(Integer, primary_key=True)
    x_pos = Column(Integer)
    y_pos = Column(Integer)
    color = Column(Enum(Color))

    tablero_id = Column(Integer, ForeignKey('tableros.id'))
    tablero = relationship("Tablero", back_populates="fichas_cajon")

    def __repr__(self) -> str:
        id = f'id={self.id!r}'
        x_pos = f'x_pos={self.x_pos!r}'
        y_pos = f'y_pos={self.y_pos!r}'
        color = f'color={self.color!r}'
        return '{' + id + ', ' + x_pos + ', ' + y_pos + ', ' + color + '}'