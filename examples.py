"""
Banco de sudokus de ejemplo para la UI y los tests.

Tres niveles:

- ``'easy'`` — ~35-40 pistas, casi obvio.
- ``'medium'`` — ~28-32 pistas.
- ``'hard'`` — 22-26 pistas, catalogado como diabólico/extreme. Pensado
  para que el backtracking clásico encadene muchos backtracks y la
  heurística MRV destaque (paso 7).

Cada puzzle viene de una fuente reputada citada en su comentario. Su
unicidad y su forma se verifican en ``tests/test_examples.py`` con
:func:`solver._count_solutions`.
"""

from __future__ import annotations


# EASY: línea 10 (índice 9) del fichero ``easy.txt`` del banco de
# sudokus grantm/sudoku-exchange-puzzle-bank en GitHub. Puzzles
# generados por QQWing y rateados con Sukaku Explainer.
# Fuente: https://raw.githubusercontent.com/grantm/sudoku-exchange-puzzle-bank/master/easy.txt
# Hash: 0004bab224ce. Rating Sukaku: 1.2 (≤1.5 = "easy" según el README
# del banco; ningún puzzle de las primeras 50 líneas tenía rating ≤1.0,
# así que se relajó el criterio a ≤1.5). 36 pistas.
EASY: list[list[int]] = [
    [0, 0, 7, 0, 2, 0, 8, 5, 0],
    [2, 0, 0, 5, 1, 6, 0, 0, 0],
    [4, 0, 0, 0, 0, 0, 0, 0, 6],
    [0, 7, 0, 6, 4, 8, 0, 9, 0],
    [9, 3, 0, 1, 0, 2, 0, 6, 8],
    [0, 6, 0, 9, 5, 3, 0, 2, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 5],
    [0, 0, 0, 4, 9, 5, 0, 0, 2],
    [0, 2, 9, 0, 6, 0, 1, 0, 0],
]


# MEDIUM: el sudoku canónico del artículo "Sudoku" en la Wikipedia
# inglesa, presente en la página desde 2005 (fichero
# ``Sudoku_Puzzle_by_L2G-20050714_standardized_layout.svg``). Es uno
# de los puzzles más citados como ejemplo introductorio en literatura
# sobre sudokus.
# Fuente: https://en.wikipedia.org/wiki/Sudoku
# 30 pistas.
MEDIUM: list[list[int]] = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


# HARD: "AI Escargot" de Arto Inkala (2006). Famoso por haber sido
# anunciado en su día como "el sudoku más difícil del mundo"; sigue
# siendo benchmark recurrente para solvers porque exige cadenas de
# deducción profundas. Se usa la transcripción "corregida" publicada
# en SudokuWiki (un dígito erróneo se corrigió tras años en
# circulación).
# Fuente: https://www.sudokuwiki.org/Escargot
# 23 pistas.
HARD: list[list[int]] = [
    [1, 0, 0, 0, 0, 7, 0, 9, 0],
    [0, 3, 0, 0, 2, 0, 0, 0, 8],
    [0, 0, 9, 6, 0, 0, 5, 0, 0],
    [0, 0, 5, 3, 0, 0, 9, 0, 0],
    [0, 1, 0, 0, 8, 0, 0, 0, 2],
    [6, 0, 0, 0, 0, 4, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 4, 0, 0, 0, 0, 0, 0, 7],
    [0, 0, 7, 0, 0, 0, 3, 0, 0],
]


EXAMPLES: dict[str, list[list[int]]] = {
    "easy": EASY,
    "medium": MEDIUM,
    "hard": HARD,
}
