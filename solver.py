"""
Solver de Sudoku con backtracking.

Dos estrategias:
1. Clásico: prueba celdas en orden de lectura
2. MRV (Minimum Remaining Values): elige la celda con menos candidatos primero

Convenciones:
Tablero: lista de listas de enteros de 9x9. (board[row][col])
0 = celda vacía
1-9 = números fijos
"""

import copy

# ===============================================================
# VALIDACIÓN
# ========================================================

def is_valid_board(board):
    """ Comprueba si el tablero es válido (sin duplicados).
    Devuelve siempre una tupla (bool, str): (True, "") si es válido,
    o (False, mensaje) describiendo el primer conflicto encontrado."""
    #Comprobar que no hay duplicados en las filas
    for r in range(9):
        seen = set()                     #Conjunto para recordar números vistos
        for c in range(9):
            v = board[r][c]
            if v == 0:                   #Saltar celdas vacías
                continue
            if v in seen:                #Si ya vimos este número en esta fila
                return False, f"Número {v} duplicado en la fila {r + 1}"
            seen.add(v)                  #Recordar este número

    # Comprobar que no hay duplicados en las columnas
    for c in range(9):
        seen = set()
        for r in range(9):
            v = board[r][c]
            if v == 0:
                continue
            if v in seen:
                return False, f"Número {v} duplicado en la columna {c + 1}"
            seen.add(v)

    # Comprobar que no hay duplicados en los bloques 3x3
    for br in range(3):                  # br = bloque fila (0,1,2)
        for bc in range(3):              # bc = bloque columna (0,1,2)
            seen = set()
            # Recorrer las 9 celdas del bloque actual
            for r in range(br * 3, br * 3 + 3):
                for c in range(bc * 3, bc * 3 + 3):
                    v = board[r][c]
                    if v == 0:
                        continue
                    if v in seen:
                        return False, f"Número {v} duplicado en el bloque 3x3 ({br + 1}, {bc + 1})"
                    seen.add(v)

    return True, ""                     # Todo válido


def is_solved(board):
    """Indica si el tablero está completamente resuelto."""
    valid, _ = is_valid_board(board)     #Primero comprobar que es válido
    if not valid:
        return False
    # Comprobar que no hay ningún 0 (celda vacía)
    for row in board:
        if 0 in row:
            return False
    return True

def candidates(board, row, col):
    """Devuelve el conjunto de valores 1-9 que pueden ir en (row, col).
    Si la celda ya tiene valor, devuelve conjunto vacío. """
    if board[row][col] != 0:             #Si ya está ocupada
        return set()                     #No hay candidatos
    
    used = set()                         #Conjunto de números que NO pueden ir
    
    #Añadir números de la misma fila
    for k in range(9):
        used.add(board[row][k])
    
    #Añadir números de la misma columna
    for k in range(9):
        used.add(board[k][col])
    
    # Añadir números del mismo bloque 3x3
    br = (row // 3) * 3                  #Fila inicial del bloque (0,3,6)
    bc = (col // 3) * 3                  #Columna inicial del bloque (0,3,6)
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            used.add(board[r][c])
    
    #Devolver los números del 1 al 9 que NO están en USED
    result = set()
    for v in range(1, 10):
        if v not in used:
            result.add(v)
    return result

# ======================================================================
# SELECCIÓN DE CELDA VACÍA
# =============================================================

#Para clasico
def find_empty(board):
    """ Devuelve la primera celda vacía en orden de lectura.
    Recorre filas de arriba abajo, y dentro de cada fila de izquierda a derecha. """
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:         #Encontrar una celda vacía
                return r, c              #Devolver sus coordenadas
    return None                          #No hay celdas vacías

#Para MRV
def find_empty_mrv(board):
    """ Devuelve la celda vacía con menos candidatos (MRV).
    Si hay empate, elige la primera en orden de lectura. """
    best = None                          #Mejor celda encontrada
    best_count = 10                      #Inicializar con valor > 9
    
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:         #Saltar celdas ocupadas
                continue
            n = len(candidates(board, r, c))  #Número de candidatos
            if n < best_count:           #Si encontramos una con menos candidatos
                best = (r, c)            #Guardar sus coordenadas
                best_count = n           #Actualizar el mínimo
    return best                          #Devolver la mejor celda (o None si no hay)


# =============================================================
# BACKTRACKING (clásico y MRV unificados)
# ===============================================================

def _solve_recursive(board, find_cell):
    """Backtracking parametrizado por la estrategia de selección de celda.
    `find_cell` debe ser find_empty (clásico) o find_empty_mrv (MRV).
    Modifica el tablero IN-PLACE. Devuelve True si encuentra solución."""
    cell = find_cell(board)
    if cell is None:                     # Sin celdas vacías -> resuelto
        return True

    row, col = cell

    for value in sorted(candidates(board, row, col)):
        board[row][col] = value
        if _solve_recursive(board, find_cell):
            return True
        board[row][col] = 0              # Backtrack

    return False


def _solve_classic(board):
    """Backtracking clásico (primera celda vacía, probar 1..9)."""
    return _solve_recursive(board, find_empty)


def solve_mrv(board):
    """Backtracking con heurística MRV (celda con menos candidatos primero)."""
    return _solve_recursive(board, find_empty_mrv)

# ===================================================================
#Al hacer modificaciones debi implementar esta parte para que la UI pueda mostrar el proceso paso a paso.
#Esta parte va ser omitida en la presentacion, es para asegurar que la UI funcione correctamente.
#No es parte del algoritmo de backtracking. Es solo visualizacion.
class Step:
    """
    Evento atómico para la UI.
    Cada paso representa una acción del algoritmo.
    """
    def __init__(self, row, col, value, action, steps_count, backtracks_count):
        self.row = row                    # Fila 0-8 (0 si action es 'done'/'fail')
        self.col = col                    # Columna 0-8 (0 si action es 'done'/'fail')
        self.value = value                # Valor 1-9 (0 si action es 'done'/'fail')
        self.action = action              # 'try', 'place', 'remove', 'done', 'fail'
        self.steps_count = steps_count    # Número total de intentos hasta ahora
        self.backtracks_count = backtracks_count  # Número total de retrocesos


def _search_iter(board, counters, find_cell):
    """
    Generador interno de backtracking.
    Emite Step para cada acción (try, place, remove).
    """
    cell = find_cell(board)              #Buscar siguiente celda vacía
    if cell is None:                     #No hay celdas vacías → éxito
        return True                      #Propagar éxito hacia arriba
    
    row, col = cell
    
    for value in sorted(candidates(board, row, col)):
        #PASO 1: Intentar el valor
        counters["steps"] = counters["steps"] + 1
        yield Step(row, col, value, "try", counters["steps"], counters["backtracks"])
        
        #PASO 2: Colocar el valor en el tablero
        board[row][col] = value
        yield Step(row, col, value, "place", counters["steps"], counters["backtracks"])
        
        #PASO 3: Recursión para resolver el resto
        result = yield from _search_iter(board, counters, find_cell)
        if result is True:               # Si la recursión tuvo éxito
            return True                  # Propagar éxito
        
        #PASO 4: Si llegamos aquí, el valor no funcionó → backtrack
        board[row][col] = 0              # Deshacer la colocación
        counters["backtracks"] = counters["backtracks"] + 1
        yield Step(row, col, value, "remove", counters["steps"], counters["backtracks"])
    
    return False                         #Ningún candidato funcionó


def _solve_generator(board, find_cell):
    """Generador parametrizado por la estrategia de selección de celda.
    Emite Step incluyendo 'done' o 'fail' al final."""
    counters = {"steps": 0, "backtracks": 0}

    if is_solved(board):
        yield Step(0, 0, 0, "done", 0, 0)
        return

    solved = yield from _search_iter(board, counters, find_cell)
    final_action = "done" if solved else "fail"
    yield Step(0, 0, 0, final_action, counters["steps"], counters["backtracks"])


_STRATEGIES = {
    "classic": find_empty,
    "mrv": find_empty_mrv,
}


#Exportar para UI
def solve_step_by_step(board, mode="classic"):
    """
    board: tablero 9x9 con 0 en celdas vacías
    mode: "classic" o "mrv"
    Devuelve un generador de Step objetos.
    """
    if mode not in _STRATEGIES:
        raise ValueError(f"Modo desconocido: {mode}")

    ok, msg = is_valid_board(board)
    if not ok:
        raise ValueError(msg)

    board_copy = copy.deepcopy(board)
    return _solve_generator(board_copy, _STRATEGIES[mode])
