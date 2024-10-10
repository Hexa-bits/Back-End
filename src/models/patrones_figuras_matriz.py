import numpy as np

"""Funcion que obtiene las coordenadas(x,y) de los 1s en una matriz"""
def convertir_matriz_1s_a_coordenadas(figura) -> list:
    coordenadas = []
    for i, fila in enumerate(figura):
        for j, valor in enumerate(fila):
            if valor == 1:
                coordenadas.append((i, j))
    return coordenadas

###################################################################

#Todas las figuras posibles
figures_list = []
#CHECKEAR QUE AL REDEDOR DE LOS ! HAYAN 0 o BORDE
#NO SE PUEDE HARDCODEAR PORQUE SUMARIA MUCHAS MAS FIGURAS POR CADA FIG REAL
#MEJOR ENCONTRARLA PRIMERO Y CHEQUEAR LUEGO


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

##########################################

"""Dado un patrón, genera las 4 rotaciones posibles"""
def generar_rotaciones(patron) -> list:
    rotaciones = [patron]
    for _ in range(3):
        rotaciones.append(np.rot90(rotaciones[-1]))  # Rotar 90 grados en sentido antihorario
    return rotaciones

"""Proceso que genera las 100 rotaciones de figuras posibles para detectar en la matriz"""
def generate_all_figures() -> list:
    all_figures = []
    for figure in figures_list:
        all_figures.extend(generar_rotaciones(figure))
    return all_figures

listita = generate_all_figures()
j = 1
for i in listita:
    #counts in the list
    print("figura numero:")
    print(j)
    j+=1
    print("#####################################")
    print(i)
    print("/////////////////////////////////////")
    print(convertir_matriz_1s_a_coordenadas(i))
    print("#####################################")