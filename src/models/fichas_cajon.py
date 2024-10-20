from src.models.color_enum import Color
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, Enum
from src.db import Base

#from src.models.tablero import Tablero
#Debe importarla Tablero a ficha cajon y no al reves
#Sino genera un bug de que tablero no encuentra la tabla ficha cajon al crearse

#NOTA A FUTURO: Quizas sea mejor tener todos los modelos en un solo archivo por problemas de dependencias

class FichaCajon(Base):
    """
    Entidad que representa a cada una de las 36 fichas cajon que conforman el
    de una partida. Posee un id unico, posiciones x e y, y un color que se 
    representa por medio de un enum. Guarda relación uno a uno con tablero.
    """
    __tablename__ = "fichas"

    id = Column(Integer, primary_key=True)
    x_pos = Column(Integer)
    y_pos = Column(Integer)
    color = Column(Enum(Color))

    tablero_id = Column(Integer, ForeignKey('tableros.id'))
    tablero = relationship("Tablero", back_populates="fichas_cajon")

    def __eq__(self, other):
        if not isinstance(other, FichaCajon):
            return False
        return (self.x_pos == other.x_pos and
                self.y_pos == other.y_pos and
                self.color == other.color and
                self.tablero_id == other.tablero_id)

    def __repr__(self) -> str:
        id = f'id={self.id!r}'
        x_pos = f'x_pos={self.x_pos!r}'
        y_pos = f'y_pos={self.y_pos!r}'
        color = f'color={self.color!r}'
        return '{' + id + ', ' + x_pos + ', ' + y_pos + ', ' + color + '}'