# Back-End

## Ejecutar en Docker:

### Crear una imagen Docker
    
    docker build -t switcher-backend .
    


### Ejecutar el contenedor
    
    docker run -d -p 8000:8000 switcher-backend
    


## Ejecutar desde la terminal:

## Es necesario crear y activar un entorno virtual

### Pasos:

- installar el gestor de entornos virtuales
   ```bash
    sudo apt install python3.12-venv

- Crear y activar entorno virtual

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

- Para instalar dependencias

    ```bash
    pip install -r requirements.txt
    ```

- Para actualizar las dependencias instaladas
    
    ```bash
    pip freeze > requeriments.txt
    ```

- Para salir del entorno virtual:
    ```bash
    deactivate
    ```
## Para correr el backend:
    
    uvicorn src.main:app --reload


## Para correr los tests
    pytest

## Para ver el coverage de los tests:
    pytest --cov=src

## Ver los detalles del missing coverage:
    pytest --cov=src --cov-report=term-missing