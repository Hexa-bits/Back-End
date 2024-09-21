from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



# Base declarativa de SQLAlchemy
Base = declarative_base()

# Crear el motor de la base de datos (aquí usamos SQLite en memoria para ejemplo)
engine = create_engine('sqlite:///mi_base_de_datos.db')

# Crear la sesión
Session = sessionmaker(bind=engine)
session = Session()

# Crear todas las tablas (esto es útil solo si las tablas aún no existen)
Base.metadata.create_all(engine)

def obtener_todas_las_partidas():
    # Consulta a la tabla 'partida' para obtener todas las filas
    partidas = session.query(Partida).all()
    return partidas

# Llamar a la función para obtener todas las partidas
partidas_guardadas = obtener_todas_las_partidas()

# Mostrar todas las partidas
for partida in partidas_guardadas:
    print(partida)
j

def list_lobbies():
    
    return