import numpy as np

# Ejemplo de matriz de 6x6 con 1s y 0s
matriz = np.array([
    [0, 1, 0, 0, 1, 0],
    [1, 0, 0, 0, 1, 0],
    [1, 0, 0, 1, 1, 1],
    [1, 1, 0, 1, 0, 1],
    [0, 0, 0, 1, 0, 1],
    [0, 0, 0, 0, 0, 1]
])

"""Función para detectar figuras usando Sliding Window (No checkea que no tengan 1s adyacentes, solo si coinciden con el patrón)"""
def detectar_patrones(matriz, patrones):
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

"""Funcion que retorna True si la figura es válida, False en caso contrario"""
def figura_valida(matriz, coords_validas):
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

from src.models.patrones_figuras_matriz import generate_all_figures

lista_patrones = generate_all_figures()

lista_patrones = [np.array(patron) for patron in lista_patrones]

# Detectar los patrones en la matriz
figuras_detectadas = detectar_patrones(matriz, lista_patrones)

# Imprimir las posiciones de los casilleros que forman cada figura "L"
for idx, figura in enumerate(figuras_detectadas, start=1):
    print(f"Figura L #{idx}: {figura}")
    if figura_valida(matriz, figura):
        print("Figura válida")
    else:
        print("Figura inválida")

    
