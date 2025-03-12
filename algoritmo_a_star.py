# algoritmo_a_star.py
import heapq

def algoritmo_a_star(inicio, objetivo, matriz):
    def heuristica(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_list = []
    heapq.heappush(open_list, (0, inicio))
    g_cost = {inicio: 0}
    came_from = {inicio: None}

    while open_list:
        _, actual = heapq.heappop(open_list)

        if actual == objetivo:
            path = []
            while came_from[actual] is not None:
                path.append(actual)
                actual = came_from[actual]
            path.append(inicio)
            path.reverse()
            return path

        for vecino in obtener_vecinos(actual, matriz):
            temp_g_cost = g_cost[actual] + 1

            if vecino not in g_cost or temp_g_cost < g_cost[vecino]:
                g_cost[vecino] = temp_g_cost
                f_cost = temp_g_cost + heuristica(vecino, objetivo)
                heapq.heappush(open_list, (f_cost, vecino))
                came_from[vecino] = actual

    return []

def obtener_vecinos(pos, matriz):
    vecinos = []
    x, y = pos
    if x > 0 and matriz[y][x - 1] == 0: 
        vecinos.append((x - 1, y))
    if x < len(matriz[0]) - 1 and matriz[y][x + 1] == 0: 
        vecinos.append((x + 1, y))
    if y > 0 and matriz[y - 1][x] == 0: 
        vecinos.append((x, y - 1))
    if y < len(matriz) - 1 and matriz[y + 1][x] == 0: 
        vecinos.append((x, y + 1))
    return vecinos
