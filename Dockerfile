# Usa una imagen base con Python
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /src

# Copia los archivos de requisitos y el resto de la aplicación
COPY requirements.txt .
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
