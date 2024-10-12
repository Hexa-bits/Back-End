from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.db import Base
from src.models.partida import Partida

class Jugador(Base):
    """
    Entidad que representa al usuario/jugador. Posee un id unico, un nombre no nulo,
    un identificar de si es anfitrion de la partida. Guarda relación uno a muchos con
    partida, y de muchos a uno con carta figura y carta movimiento. 
    """
    __tablename__ = "jugador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    es_anfitrion = Column(Boolean, default=False)

    # TO DO: ver si se puede sacar el atributo turno, ya usamos un jugador_en_turno
    # en partida que usa el mismo id del jugador para indicar el turno del mismo. 
    turno = Column(Integer, default=0)

    partida_id = Column(Integer, ForeignKey('partidas.id'), nullable=True)
    partida = relationship("Partida", back_populates="jugadores")

    cartafigura = relationship("PictureCard", back_populates="jugador")

    cartasMovimiento = relationship("MovementCard", back_populates="jugador")

    def __repr__(self) -> str:
        id = f'id={self.id!r}'
        nombre = f'nombre={self.nombre!r}'
        es_anfitrion = f'es_afirion={self.es_anfitrion!r}'
        turno = f'turno={self.turno!r}'
        return '{' +id + ', ' + nombre + ', ' + es_anfitrion + ', ' + turno + '}'
