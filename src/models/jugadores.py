from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.db import Base
from src.models.partida import Partida
class Jugador(Base):
    __tablename__ = "jugador"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    es_anfitrion = Column(Boolean, nullable=False)
    turno = Column(Integer, default=0)

    partida_id = Column(Integer, ForeignKey('partidas.id'), nullable=True)
    partida = relationship("Partida", back_populates="jugadores")

    def __repr__(self) -> str:
        id = f'id={self.id!r}'
        nombre = f'nombre={self.nombre!r}'
        es_anfitrion = f'es_afirion={self.es_anfitrion!r}'
        turno = f'turno={turno!r}'
        return id + ', ' + nombre + ', ' + es_anfitrion + ', ' + turno