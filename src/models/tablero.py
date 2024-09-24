from src.models.color_enum import Color
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Enum
from src.db import Base
from src.models.partida import Partida
from src.models.fichas_cajon import FichaCajon
class Tablero(Base):
    __tablename__ = "tableros"

    id = Column(Integer, primary_key=True)
    color_prohibido = Column(Enum(Color), nullable=True)

    partida_id = Column(Integer, ForeignKey('partidas.id'), nullable=True)
    partida = relationship("Partida", back_populates="tablero")

    fichas_cajon = relationship("FichaCajon", back_populates="tablero")

    def __repr__(self) -> str:
        id = f'id={self.id!r}'
        color_prohibido = f'color_prohibido={self.color_prohibido!r}'
        return id + ', ' + color_prohibido


