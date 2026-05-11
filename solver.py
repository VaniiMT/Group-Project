"""
Motor del solver de sudoku con backtracking.

Este módulo es independiente de la UI: expone funciones puras de validación
y consulta sobre tableros, y (en pasos posteriores) un generador paso a paso
que la interfaz consume para animar la búsqueda.

Convenciones del módulo
-----------------------
- Un tablero es una ``list[list[int]]`` de 9x9.
- El valor 0 representa una celda vacía; los valores 1-9 son las cifras del
  sudoku.
- Los índices internos ``row`` y ``col`` están en el rango 0-8.
- Los mensajes de error que devuelve :func:`is_valid_board` usan numeración
  1-9 (en lugar de 0-8) porque están pensados para mostrarse al usuario
  desde la UI.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable, Iterator


def is_valid_board(board: list[list[int]]) -> tuple[bool, str]:
    """
    Comprueba si ``board`` es un tablero de sudoku consistente.

    No exige que el tablero esté resuelto: las celdas con valor 0 (vacías)
    son legales. Lo que se valida es:

    1. Que el tablero sea una lista de 9 filas, cada una con 9 enteros.
    2. Que todos los valores estén en el rango 0-9.
    3. Que no haya duplicados de valores no nulos en ninguna fila,
       columna o bloque 3x3.

    Args:
        board: tablero candidato a validar.

    Returns:
        ``(True, '')`` si el tablero es válido.
        ``(False, mensaje)`` en caso contrario, donde ``mensaje`` es una
        cadena en español describiendo el primer problema encontrado.

    Ejemplo:
        >>> is_valid_board([[0] * 9 for _ in range(9)])
        (True, '')
        >>> ok, msg = is_valid_board([[1, 1] + [0] * 7] + [[0] * 9 for _ in range(8)])
        >>> ok
        False
    """
    # Forma 9x9.
    if not isinstance(board, list) or len(board) != 9:
        return False, "El tablero debe tener 9 filas"
    for r, row in enumerate(board):
        if not isinstance(row, list) or len(row) != 9:
            return False, f"La fila {r + 1} debe tener 9 columnas"

    # Rango de valores: enteros en 0-9.
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if not isinstance(v, int) or v < 0 or v > 9:
                return False, f"Valor inválido en ({r + 1},{c + 1}): {v!r}"

    # Duplicados en filas.
    for r in range(9):
        seen: set[int] = set()
        for c in range(9):
            v = board[r][c]
            if v == 0:
                continue
            if v in seen:
                return False, f"Duplicado en fila {r + 1}: valor {v}"
            seen.add(v)

    # Duplicados en columnas.
    for c in range(9):
        seen = set()
        for r in range(9):
            v = board[r][c]
            if v == 0:
                continue
            if v in seen:
                return False, f"Duplicado en columna {c + 1}: valor {v}"
            seen.add(v)

    # Duplicados en los nueve bloques 3x3.
    for br in range(3):
        for bc in range(3):
            seen = set()
            for r in range(br * 3, br * 3 + 3):
                for c in range(bc * 3, bc * 3 + 3):
                    v = board[r][c]
                    if v == 0:
                        continue
                    if v in seen:
                        return False, (
                            f"Duplicado en bloque ({br + 1},{bc + 1}): valor {v}"
                        )
                    seen.add(v)

    return True, ""


def is_solved(board: list[list[int]]) -> bool:
    """
    Indica si ``board`` está completamente resuelto.

    Un tablero se considera resuelto cuando es válido (cumple las reglas
    del sudoku) y no contiene ninguna celda vacía.

    Args:
        board: tablero a comprobar.

    Returns:
        ``True`` si el tablero es válido y no quedan ceros; ``False`` en
        cualquier otro caso (incluido un tablero inválido).
    """
    valid, _ = is_valid_board(board)
    if not valid:
        return False
    return count_empty(board) == 0


def count_empty(board: list[list[int]]) -> int:
    """
    Cuenta cuántas celdas vacías (valor 0) hay en ``board``.

    Esta función no valida la forma ni los valores del tablero; asume que
    ya viene en formato 9x9 con enteros. Si necesitas asegurarte, llama
    primero a :func:`is_valid_board`.

    Args:
        board: tablero 9x9.

    Returns:
        Número de celdas cuyo valor es 0.
    """
    return sum(1 for row in board for v in row if v == 0)


def candidates(board: list[list[int]], row: int, col: int) -> set[int]:
    """
    Devuelve el conjunto de valores 1-9 que pueden colocarse en
    ``(row, col)`` sin violar las reglas del sudoku.

    Para una celda ya ocupada (valor distinto de 0) devuelve un conjunto
    vacío: por convención, una celda llena no admite "candidatos".

    Esta función **no forma parte del contrato público con la UI**: se
    expone sin guion bajo únicamente para que los tests la puedan
    importar con comodidad y para reutilizarla en la heurística MRV.

    Args:
        board: tablero 9x9.
        row: índice de fila (0-8).
        col: índice de columna (0-8).

    Returns:
        Conjunto con los valores 1-9 compatibles con la celda dada.

    Ejemplo:
        >>> b = [[0] * 9 for _ in range(9)]
        >>> b[0][0] = 1
        >>> sorted(candidates(b, 0, 1))
        [2, 3, 4, 5, 6, 7, 8, 9]
    """
    if board[row][col] != 0:
        return set()

    used: set[int] = set()
    # Valores presentes en la fila y la columna.
    for k in range(9):
        used.add(board[row][k])
        used.add(board[k][col])
    # Valores presentes en el bloque 3x3.
    br, bc = (row // 3) * 3, (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            used.add(board[r][c])

    return {v for v in range(1, 10) if v not in used}


def find_empty(board: list[list[int]]) -> tuple[int, int] | None:
    """
    Localiza la primera celda vacía en orden de lectura.

    Recorre el tablero fila a fila, de izquierda a derecha, y devuelve
    la posición de la primera celda con valor 0.

    Args:
        board: tablero 9x9.

    Returns:
        Una tupla ``(row, col)`` con la primera celda vacía, o ``None``
        si el tablero ya está completo.
    """
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def find_empty_mrv(board: list[list[int]]) -> tuple[int, int] | None:
    """
    Localiza la celda vacía con menos candidatos (heurística MRV).

    MRV (*Minimum Remaining Values*) es la regla de selección de celda
    que prefiere, en cada nivel de la recursión, la celda con el menor
    número de valores 1-9 compatibles con fila, columna y bloque. La
    idea es atacar primero las celdas más restringidas: o bien hay un
    *naked single* (un único candidato, colocación forzada) o bien se
    podan ramas inválidas mucho antes que en orden de lectura.

    En caso de empate (varias celdas con el mismo recuento mínimo),
    se elige la primera en orden de lectura: el recorrido es fila a
    fila e izquierda a derecha, y la comparación usa ``<`` estricto.

    Si alguna celda vacía tiene **0 candidatos**, se devuelve igualmente.
    Esa es la propiedad *fail-fast* de MRV: el llamador iterará sobre un
    conjunto de candidatos vacío y backtrackeará de inmediato, sin
    desperdiciar trabajo explorando ramas que sabemos muertas.

    Args:
        board: tablero 9x9.

    Returns:
        Una tupla ``(row, col)`` con la celda elegida, o ``None`` si el
        tablero ya está completo.

    Ejemplo:
        >>> b = [[0] * 9 for _ in range(9)]
        >>> b[0][:8] = [1, 2, 3, 4, 5, 6, 7, 8]  # (0,8) admite solo el 9
        >>> find_empty_mrv(b)
        (0, 8)
    """
    best: tuple[int, int] | None = None
    best_count = 10  # estrictamente mayor que cualquier len(candidates(...))
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                continue
            n = len(candidates(board, r, c))
            if n < best_count:
                best = (r, c)
                best_count = n
    return best


def _solve_classic(board: list[list[int]]) -> bool:
    """
    Resuelve ``board`` con backtracking clásico recursivo plano.

    Función interna: **no forma parte del contrato público con la UI.**
    Sirve como referencia ("stepping stone") para el generador
    :func:`solve_step_by_step`, que se construirá sobre esta misma idea
    pero emitiendo ``Step`` y manteniendo contadores.

    Estrategia:

    - Selección de celda: la primera vacía en orden de lectura
      (la que devuelve :func:`find_empty`).
    - Selección de valor: candidatos válidos en orden ascendente
      (1, 2, 3, ...). Se itera ``sorted(candidates(...))`` para que el
      orden sea determinista.

    Args:
        board: tablero 9x9. **Se modifica in-place.**

    Returns:
        ``True`` si encuentra solución; en ese caso ``board`` queda con
        la solución colocada.
        ``False`` si no hay solución; en ese caso ``board`` queda
        exactamente igual que al entrar (las colocaciones se deshacen
        durante el backtrack hasta la raíz).

    Notas:
        El generador público :func:`solve_step_by_step` (paso 4)
        envolverá esta lógica con un ``deepcopy`` defensivo del tablero
        del usuario, de modo que la mutación in-place de aquí nunca
        llega a afectar a quien llama desde la UI.
    """
    cell = find_empty(board)
    if cell is None:
        return True
    row, col = cell
    for value in sorted(candidates(board, row, col)):
        board[row][col] = value
        if _solve_classic(board):
            return True
        board[row][col] = 0
    return False


@dataclass
class Step:
    """
    Evento atómico emitido por :func:`solve_step_by_step`.

    Attributes:
        row: fila 0-8 de la celda implicada (0 si ``action`` es
            ``'done'`` o ``'fail'``).
        col: columna 0-8 de la celda implicada (0 si ``action`` es
            ``'done'`` o ``'fail'``).
        value: valor 1-9 que se está probando o colocando (0 si
            ``action`` es ``'done'`` o ``'fail'``).
        action: una de ``{'try', 'place', 'remove', 'done', 'fail'}``.
        steps_count: número total acumulado de ``try`` emitidos hasta
            este Step (inclusive si ``action == 'try'``).
        backtracks_count: número total acumulado de ``remove`` emitidos
            hasta este Step (inclusive si ``action == 'remove'``).

    Convención de emisión:

    - ``try``: el algoritmo está probando ``value`` en ``(row, col)``.
      Es la única acción que incrementa ``steps_count``.
    - ``place``: el valor probado se acepta provisionalmente y queda
      en el tablero. Se emite **inmediatamente después** del ``try``,
      antes de bajar a la recursión. No incrementa ningún contador.
    - ``remove``: backtrack. Se quita el valor de la celda. Es la
      única acción que incrementa ``backtracks_count``.
    - ``done``: tablero resuelto. Sale una sola vez al final.
    - ``fail``: no hay solución. Sale una sola vez al final.
    """

    row: int
    col: int
    value: int
    action: str
    steps_count: int
    backtracks_count: int


@dataclass
class _Counters:
    """Contadores acumulados que se pasan por la recursión."""

    steps: int = 0
    backtracks: int = 0


def _search_iter(
    board: list[list[int]],
    counters: _Counters,
    find_cell: Callable[[list[list[int]]], tuple[int, int] | None],
) -> Iterator[Step]:
    """
    Generador interno de backtracking parametrizado por el selector de celda.

    La estrategia de búsqueda (clásica u MRV) queda determinada por la
    función ``find_cell`` que se le pase: :func:`find_empty` para el
    modo classic, :func:`find_empty_mrv` para MRV. La lógica de
    ``try``/``place``/``remove`` y la actualización de contadores es
    idéntica en ambos modos; lo único que cambia es a qué celda salta
    la búsqueda en cada nivel de la recursión.

    Convención sobre el valor de retorno (capturable con
    ``yield from``): ``True`` si esta rama de la búsqueda termina con
    el tablero resuelto; ``False`` si esta rama agota sus candidatos
    sin éxito. El llamador
    (:func:`_solve_classic_generator` o :func:`_solve_mrv_generator`)
    usa ese bool para decidir si emitir un ``done`` o un ``fail`` final.

    Args:
        board: tablero de trabajo. Se modifica in-place; el llamador
            es responsable de haber hecho ``deepcopy`` si quiere
            preservar el original.
        counters: contadores acumulados, mutados in-place al emitir
            ``try`` y ``remove``.
        find_cell: función que recibe el tablero y devuelve la próxima
            celda vacía a expandir, o ``None`` si no quedan vacías.

    Yields:
        Step: eventos ``try``, ``place`` y ``remove`` durante la
        búsqueda. NO emite ``done`` ni ``fail`` (eso lo hace el
        envoltorio).
    """
    cell = find_cell(board)
    if cell is None:
        return True
    row, col = cell
    for value in sorted(candidates(board, row, col)):
        counters.steps += 1
        yield Step(row, col, value, "try", counters.steps, counters.backtracks)
        board[row][col] = value
        yield Step(row, col, value, "place", counters.steps, counters.backtracks)
        if (yield from _search_iter(board, counters, find_cell)):
            return True
        board[row][col] = 0
        counters.backtracks += 1
        yield Step(
            row, col, value, "remove", counters.steps, counters.backtracks
        )
    return False


def _solve_classic_generator(board: list[list[int]]) -> Iterator[Step]:
    """
    Generador que produce el stream de Step para el modo classic.

    Asume que ``board`` ya viene **validado y deep-copiado** por el
    envoltorio público :func:`solve_step_by_step`. Aquí solo decide
    el caso "ya resuelto" y orquesta la búsqueda + cierre con
    ``done``/``fail``. La estrategia (selector de celda) se inyecta en
    :func:`_search_iter` como :func:`find_empty`.
    """
    counters = _Counters()
    if is_solved(board):
        # Tablero ya resuelto: un único Step done con todo a cero.
        yield Step(0, 0, 0, "done", 0, 0)
        return
    solved = yield from _search_iter(board, counters, find_empty)
    final_action = "done" if solved else "fail"
    yield Step(
        0, 0, 0, final_action, counters.steps, counters.backtracks
    )


def _solve_mrv_generator(board: list[list[int]]) -> Iterator[Step]:
    """
    Generador que produce el stream de Step para el modo MRV.

    Mismo contrato que :func:`_solve_classic_generator` (asume tablero
    validado y deep-copiado por :func:`solve_step_by_step`), pero la
    estrategia inyectada en :func:`_search_iter` es
    :func:`find_empty_mrv`: en cada nivel de la recursión se elige
    la celda vacía con menos candidatos en lugar de la primera en orden
    de lectura.
    """
    counters = _Counters()
    if is_solved(board):
        # Tablero ya resuelto: un único Step done con todo a cero.
        yield Step(0, 0, 0, "done", 0, 0)
        return
    solved = yield from _search_iter(board, counters, find_empty_mrv)
    final_action = "done" if solved else "fail"
    yield Step(
        0, 0, 0, final_action, counters.steps, counters.backtracks
    )


def solve_step_by_step(
    board: list[list[int]], mode: str = "classic"
) -> Iterator[Step]:
    """
    Resuelve ``board`` paso a paso, emitiendo un :class:`Step` por
    acción del backtracking.

    Punto de entrada **público** del solver. La UI lo consume como un
    generador, animando la búsqueda Step a Step.

    La función NO es generadora: valida ``mode`` y ``board`` de forma
    eager (las excepciones saltan en el momento de la llamada, no al
    primer ``next()``) y devuelve el generador interno trabajando
    sobre una copia profunda del tablero, de modo que el tablero del
    usuario nunca se modifica.

    Args:
        board: tablero 9x9 con 0 en celdas vacías y 1-9 en pistas.
        mode: ``'classic'`` (backtracking en orden de lectura) o
            ``'mrv'`` (Minimum Remaining Values: en cada nivel se elige
            la celda vacía con menos candidatos; ver
            :func:`find_empty_mrv`).

    Returns:
        Un iterador de :class:`Step`. El último Step siempre tiene
        ``action='done'`` (tablero resuelto) o ``action='fail'``
        (tablero válido pero sin solución).

    Raises:
        ValueError: si ``board`` no pasa :func:`is_valid_board`, o si
            ``mode`` es un valor desconocido.

    Ejemplo:
        >>> for step in solve_step_by_step(my_board):
        ...     ui.render(step)
    """
    if mode not in ("classic", "mrv"):
        raise ValueError(f"Modo desconocido: {mode!r}")

    ok, msg = is_valid_board(board)
    if not ok:
        raise ValueError(msg)

    if mode == "classic":
        return _solve_classic_generator(copy.deepcopy(board))
    return _solve_mrv_generator(copy.deepcopy(board))


def _count_solutions(board: list[list[int]], limit: int = 2) -> int:
    """
    Cuenta hasta ``limit`` soluciones distintas de ``board`` y para.

    Es la herramienta básica para verificar **unicidad** de un sudoku
    candidato a publicación: con ``limit=2`` el resultado distingue
    "0 soluciones" / "exactamente 1" / "≥2".

    No muta ``board``: trabaja sobre una copia profunda interna.

    Args:
        board: tablero 9x9 a analizar.
        limit: cota superior del recuento; la búsqueda corta en cuanto
            la alcanza.

    Returns:
        ``min(soluciones_reales, limit)``.
    """
    work = copy.deepcopy(board)
    count = 0

    def _recurse() -> None:
        nonlocal count
        if count >= limit:
            return
        cell = find_empty(work)
        if cell is None:
            count += 1
            return
        row, col = cell
        for value in sorted(candidates(work, row, col)):
            work[row][col] = value
            _recurse()
            work[row][col] = 0
            if count >= limit:
                return

    _recurse()
    return count
