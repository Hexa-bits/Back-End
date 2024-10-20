import numpy as np

def generar_rotaciones(patron) -> list[np.ndarray]:
    """Dado un patrón, genera las 4 rotaciones posibles"""

    rotaciones = [patron]
    for _ in range(3):
        rotaciones.append(np.rot90(rotaciones[-1]))  # Rotar 90 grados en sentido antihorario
    return rotaciones

def generate_all_figures() -> list[np.ndarray]:
    """Proceso que genera las 100 rotaciones de figuras posibles para detectar en la matriz"""

    #Generamos todas las figuras rotadas posibles (100 en total)
    #Primero agregamos las figuras sin rotar (25 figuras)
    figures_list = pictureCardsFigures()

    all_figures = []

    #Agregamos todas las rotaciones posibles de las figuras

    for figure in figures_list:
        all_figures.extend(generar_rotaciones(figure))
        
    return all_figures

def pictureCardsFigures() -> list[np.ndarray]:
    figures_list = []

    # 18 FIGURAS DIFICILES
    fig01 = [
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 0]
    ]
    figures_list.append(fig01)

    fig02 = [
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 1]
    ]
    figures_list.append(fig02)

    fig03 = [
        [0, 0, 1, 1],
        [0, 0, 1, 0],
        [1, 1, 1, 0]
    ]
    figures_list.append(fig03)

    fig04 = [
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 1]
    ]
    figures_list.append(fig04)

    fig05 = [
        [1, 1, 1, 1, 1],
    ]
    figures_list.append(fig05)

    fig06 = [
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1]
    ]
    figures_list.append(fig06)

    fig07 = [
        [1, 1, 1, 1],
        [0, 0, 0, 1],
    ]
    figures_list.append(fig07)

    fig08 = [
        [1, 1, 1, 1],
        [1, 0, 0, 0],
    ]
    figures_list.append(fig08)

    fig09 = [
        [0, 0, 1],
        [1, 1, 1],
        [0, 1, 0]
    ]
    figures_list.append(fig09)

    fig10 = [
        [0, 0, 1],
        [1, 1, 1],
        [1, 0, 0]
    ]
    figures_list.append(fig10)

    fig11 = [
        [1, 0, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]
    figures_list.append(fig11)

    fig12 = [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 1]
    ]
    figures_list.append(fig12)

    fig13 = [
        [1, 1, 1, 1],
        [0, 0, 1, 0]
    ]
    figures_list.append(fig13)

    fig14 = [
        [1, 1, 1, 1],
        [0, 1, 0, 0]
    ]
    figures_list.append(fig14)

    fig15 = [
        [0, 1, 1],
        [1, 1, 1],
    ]
    figures_list.append(fig15)

    fig16 = [
        [1, 0, 1],
        [1, 1, 1],
    ]
    figures_list.append(fig16)

    fig17 = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]
    figures_list.append(fig17)

    fig18 = [
        [1, 1, 1],
        [0, 1, 1],
    ]
    figures_list.append(fig18)

    # 7 FIGURAS FACILES

    fig19 = [
        [0, 1, 1],
        [1, 1, 0]
    ]
    figures_list.append(fig19)

    fig20 = [
        [1, 1],
        [1, 1]
    ]
    figures_list.append(fig20)

    fig21 = [
        [1, 1, 0],
        [0, 1, 1]
    ]
    figures_list.append(fig21)

    fig22 = [
        [0, 1, 0],
        [1, 1, 1]
    ]
    figures_list.append(fig22)

    fig23 = [
        [1, 1, 1],
        [0, 0, 1],
    ]
    figures_list.append(fig23)

    fig24 = [
        [1, 1, 1, 1],
    ]
    figures_list.append(fig24)

    fig25 = [
        [0, 0, 1],
        [1, 1, 1],
    ]
    figures_list.append(fig25)

    return figures_list