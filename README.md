# Back-End

## EJECUTAR LA APP:

### Crear una imagen Docker
    ```bash
    docker build -t my-fastapi-app .
    ```

### Construir la imagen de Docker
    ```bash
    docker build -t my-fastapi-app .
    ```

### Ejecutar el contenedor
    ```bash
    docker run -d --name my-fastapi-container -p 8000:8000 my-fastapi-app
    ```


## EJECUTAR DESDE LA TERMINAL:

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
    ```bash
    uvicorn src.main:app --reload

    ```
