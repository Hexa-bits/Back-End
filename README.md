# Back-End

## Crear y activar un entorno virtual

Conflictos de versiones entre colaboradores.

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
- Para correr el backend:
    ```bash
    uvicorn src.main:app --reload

    ```
