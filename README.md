# Back-End

## Crear y activar un entorno virtual

Conflictos de versiones entre colaboradores.

### Pasos:

- Crear y activar entorno virtual

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

- Para instalar dependencias

    ```bash
    pip install -r requirements
    ```

- Para actualizar las dependencias instaladas
    
    ```bash
    pip freeze > requeriments.txt
    ```

- Para salir del entorno virtual:
    ```bash
    deactivate
    ```