import numpy as np

def detectar_patrones(matriz, patrones) -> list:
    """Función para detectar figuras usando Sliding Window (No checkea que no tengan 1s adyacentes, solo si coinciden con el patrón)
    Devuelve una lista de listas de coordenadas de las figuras detectadas.
    """

    filas, columnas = matriz.shape
    figuras_detectadas = []  # Almacena las posiciones de las figuras encontradas
    
    # Recorrer cada patrón
    for patron in patrones:
        p_filas, p_columnas = patron.shape  # Tamaño del patrón

        # Desplazar la ventana sobre la matriz
        for i in range(filas - p_filas + 1):
            for j in range(columnas - p_columnas + 1):
                # Extraer la submatriz de la ventana deslizante
                submatriz = matriz[i:i + p_filas, j:j + p_columnas]
                
                # Comparar submatriz con el patrón
                if np.array_equal(submatriz, patron):
                    # Si coinciden, guardar las coordenadas
                    coords = [(i + x, j + y) for x in range(p_filas) for y in range(p_columnas) if patron[x, y] == 1]
                    figuras_detectadas.append(coords)

    return figuras_detectadas

def figura_valida(matriz, coords_validas) -> bool:
    """Funcion que retorna True si la figura es válida, False en caso contrario"""

    filas, columnas = matriz.shape
    coordenadas_set = set(coords_validas)  # Convertir la lista en un set para búsquedas rápidas
    
    # Direcciones de los 4 vecinos adyacentes: arriba, abajo, izquierda, derecha
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for coord in coords_validas:
        x, y = coord
        
        # Revisar vecinos en las 4 direcciones
        for dx, dy in direcciones:
            nx, ny = x + dx, y + dy
            
            # Si el vecino está dentro de los límites de la matriz
            if 0 <= nx < filas and 0 <= ny < columnas:
                # Si el vecino es un 1 y no está en la lista de coordenadas válidas
                if matriz[nx, ny] == 1 and (nx, ny) not in coordenadas_set:
                    return False  # Hay un 1 no válido adyacente
    return True  # Todos los vecinos son válidos

def separar_matrices_por_color(matriz, lista_colores) -> list:
    """Separa la matriz de colores en matrices individuales por color.
    Toma como elementos:
    matriz: Una matriz numpy donde cada elemento representa un color.
    lista_colores: Una lista de colores presentes en la matriz.
    
    Devuelve una lista de matrices, donde cada matriz representa un color.
    """

    # Obtener las dimensiones de la matriz
    filas, columnas = matriz.shape

    # Crear una lista vacía para almacenar las matrices de colores
    matrices_colores = []   
    # Iterar sobre cada color
    for color in lista_colores:
        # Crear una matriz de ceros con las mismas dimensiones
        matriz_color = np.zeros((filas, columnas))
        # Asignar 1 en las posiciones donde el color coincide (matriz==color)
        matriz_color[matriz == color] = 1
        # Agregar la matriz de color a la lista
        matrices_colores.append(matriz_color)   
    return matrices_colores 