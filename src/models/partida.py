from sqlalchemy import Column, String, Integer, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from src.db import Base


class Partida(Base):
    __tablename__ = "partidas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    cantidad_max_jugadores = Column(Integer, nullable=False)
    cantidad_min_jugadores = Column(Integer, nullable=False)
    jugador_en_turno = Column(Integer, default=0)
    partida_iniciada = Column(Boolean, default=False)

    cartafigura = relationship("pictureCard", back_populates="partida")

    def __repr__(self) -> str:
        id = f'id={self.id!r}'
        nombre = f'nombre={self.nombre!r}'
        cantidad_jugadores = f'cantidad_max_jugadores={self.cantidad_max_jugadores!r}, cantidad_min_jugadores={self.cantidad_min_jugadores!r}'
        jugador_en_turno = f'jugador_en_turno={self.jugador_en_turno!r}'
        partida_iniciada = f'partida_iniciada={self.partida_iniciada}'
        return id + ', ' + nombre + ', ' + cantidad_jugadores + ', ' + jugador_en_turno + ', ' + partida_iniciada
    
    __table_args__ = (
        CheckConstraint('cantidad_max_jugadores BETWEEN 2 AND 4', name='cantidad_max_check'),
        CheckConstraint('cantidad_min_jugadores BETWEEN 2 AND 4', name='cantidad_min_check'),
    )
