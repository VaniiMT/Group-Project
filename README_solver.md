# Solver de Sudoku — Módulo de Juan (Integrante 1)

Este documento explica cómo usar `solver.py` y `examples.py` desde los otros módulos
del proyecto. Está escrito para que cualquier compañero del equipo pueda integrar
el motor sin tener que leer el código por dentro.

## Resumen en una frase

`solve_step_by_step(board, mode)` es un generador que emite eventos `Step` por
cada acción del backtracking (probar un valor, colocarlo, retroceder). La UI lo
consume paso a paso para animar la búsqueda.

---

## Qué hay en mis ficheros

- **`solver.py`** — el motor. Validación de tableros, dos algoritmos
  (backtracking clásico y backtracking con heurística MRV), y el generador
  público que consume la UI.
- **`examples.py`** — tres sudokus de ejemplo (fácil, medio, difícil) con
  solución única verificada.

---

## API pública (lo único que tenéis que importar)

```python
from solver import solve_step_by_step, Step, is_valid_board, is_solved, count_empty
from examples import EXAMPLES, EASY, MEDIUM, HARD
```

### `solve_step_by_step(board, mode='classic') -> Iterator[Step]`

La función estrella. Recibe un tablero 9x9 y un modo de algoritmo, y devuelve
un generador que emite un `Step` por cada acción del solver.

**Argumentos:**

- `board`: lista de listas 9x9. Un `0` representa una celda vacía; valores
  `1-9` son pistas.
- `mode`: `'classic'` (backtracking en orden de lectura) o `'mrv'`
  (Minimum Remaining Values, más eficiente).

**Devuelve:** un iterador de `Step`. El último Step siempre tiene
`action='done'` (resuelto) o `action='fail'` (sin solución).

**Lanza:**

- `ValueError` si el tablero no es válido (forma incorrecta, valores fuera de
  rango, duplicados en fila/columna/bloque). Las excepciones saltan en el
  momento de la llamada, **no al primer `next()`** — esto es importante para
  que la UI pille los errores antes de empezar a animar.
- `ValueError` si el `mode` es un valor desconocido.

**Importante:** la función no muta el tablero que le pasáis. Internamente
trabaja sobre una copia profunda.

### `Step` (dataclass)

Cada evento que emite el generador. Atributos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `row` | `int` | Fila 0-8 de la celda implicada (0 si action='done'/'fail') |
| `col` | `int` | Columna 0-8 de la celda implicada (0 si action='done'/'fail') |
| `value` | `int` | Valor 1-9 que se prueba/coloca/quita (0 si action='done'/'fail') |
| `action` | `str` | Una de `'try'`, `'place'`, `'remove'`, `'done'`, `'fail'` |
| `steps_count` | `int` | Total acumulado de intentos hasta este Step |
| `backtracks_count` | `int` | Total acumulado de retrocesos hasta este Step |

### Acciones del `Step`

| `action` | Qué significa | Qué debe hacer la UI |
|----------|---------------|----------------------|
| `try` | Se está PROBANDO `value` en `(row, col)` | Mostrar el valor en gris claro / tentativa |
| `place` | El valor se acepta provisionalmente y queda en el tablero | Pintar el valor en color definitivo |
| `remove` | Backtrack: se quita el valor de la celda | Borrar visualmente la celda |
| `done` | Tablero resuelto. `(row, col, value) == (0, 0, 0)` | Mostrar mensaje "resuelto", parar animación |
| `fail` | Sin solución. `(row, col, value) == (0, 0, 0)` | Mostrar mensaje "sin solución", parar animación |

**Convención importante sobre los contadores:**

- Solo `try` incrementa `steps_count`.
- Solo `remove` incrementa `backtracks_count`.
- `place`, `done` y `fail` no tocan ningún contador.
- En el `Step` final (`done` o `fail`), los contadores llevan el valor total
  acumulado de toda la búsqueda. Esto es lo que Persona 3 puede guardar en el
  CSV.

### Funciones auxiliares públicas

```python
is_valid_board(board) -> tuple[bool, str]
```
Devuelve `(True, '')` si el tablero es válido. Si no lo es, devuelve
`(False, mensaje)` con un mensaje listo para mostrar al usuario (en español,
con coordenadas 1-indexadas).

```python
is_solved(board) -> bool
```
`True` si el tablero está completo y respeta las reglas.

```python
count_empty(board) -> int
```
Número de celdas vacías (con valor 0).

---

## Ejemplo de uso desde la UI

Así es como Persona 2 (UI) consume el generador:

```python
from solver import solve_step_by_step, Step
from examples import EXAMPLES
import copy

# Tablero del usuario (o uno de ejemplo)
board = copy.deepcopy(EXAMPLES['hard'])

# Crear el generador (las excepciones de validación saltan AQUÍ)
try:
    generator = solve_step_by_step(board, mode='mrv')
except ValueError as e:
    print(f"Tablero inválido: {e}")
    return

# Consumir paso a paso
for step in generator:
    if step.action == 'try':
        # mostrar tentativa en gris
        pass
    elif step.action == 'place':
        board[step.row][step.col] = step.value  # actualizar visualmente
    elif step.action == 'remove':
        board[step.row][step.col] = 0  # borrar visualmente
    elif step.action == 'done':
        print(f"Resuelto en {step.steps_count} pasos, {step.backtracks_count} retrocesos")
    elif step.action == 'fail':
        print("Sin solución")
```

### Animación con Tkinter (para Persona 2)

Para no congelar la UI durante la resolución, NO uses `for step in generator`
en un solo `tick`. Usa el patrón `root.after()`:

```python
def step_animation():
    if self.cancelled:
        return  # el usuario pulsó cancelar
    try:
        step = next(self.generator)
    except StopIteration:
        return  # el generador terminó (ya hubo done/fail antes)

    # actualizar UI según step.action
    self.render(step)

    # programar el siguiente paso según el modo
    delay = MODE_DELAYS[self.current_mode]
    self.root.after(delay, step_animation)
```

---

## Sudokus de ejemplo (`examples.py`)

```python
from examples import EXAMPLES, EASY, MEDIUM, HARD
```

`EXAMPLES` es un diccionario con tres claves:

| Clave | Pistas | Fuente |
|-------|--------|--------|
| `'easy'` | 36 | Banco grantm/sudoku-exchange-puzzle-bank |
| `'medium'` | 30 | Sudoku canónico de Wikipedia |
| `'hard'` | 23 | "AI Escargot" de Arto Inkala (2006) |

Los alias `EASY`, `MEDIUM` y `HARD` apuntan al mismo contenido para quien
prefiera importarlos directamente.

Los tres puzzles tienen **solución única** verificada con la función interna
`_count_solutions`.

---

## ¿Por qué dos algoritmos?

El brief del proyecto pide comparar el backtracking clásico con una mejora
heurística. He implementado MRV (Minimum Remaining Values): en cada paso, en
vez de elegir la siguiente celda vacía en orden de lectura, MRV elige la
celda con MENOS candidatos válidos. Si una celda solo admite un número, lo
coloca ya; si admite muchos, la deja para más tarde.

**El resultado sobre el sudoku difícil (AI Escargot, 23 pistas):**

| Modo | Pasos (tries) | Retrocesos (backtracks) |
|------|---------------|-------------------------|
| `classic` | 8969 | 8911 |
| `mrv` | 217 | 159 |
| **Mejora** | **~41x** | **~56x** |

Esto es lo que justifica que merezca la pena implementar la heurística. Para
la memoria teórica de Persona 4 y para el CSV de Persona 3, son los números
clave.

---

## Cosas a tener en cuenta

1. **El generador no se puede reiniciar.** Si lo consumís hasta el final
   (`done`/`fail`), tenéis que crear uno nuevo con
   `solve_step_by_step(board, mode)` para resolver otra vez.

2. **El tablero original no se modifica.** Si queréis ver el tablero resuelto
   tenéis que aplicar los `place`/`remove` a una copia vuestra mientras
   consumís el generador (ver ejemplo arriba). La UI ya lo hace de forma
   natural al animar.

3. **MRV puede devolver una celda con 0 candidatos.** Es intencionado: es la
   propiedad fail-fast de la heurística. La búsqueda retrocederá
   inmediatamente al ver que no hay valores que probar.

4. **El modo classic es determinista.** Para un mismo tablero, siempre
   produce la misma secuencia exacta de Steps. Útil para tests reproducibles.

---

## ¿Algo no funciona como esperabais?

Avisadme. El contrato está cerrado pero si veis algún caso que no he
contemplado lo añadimos. Los detalles del comportamiento esperado están
documentados en los docstrings dentro de `solver.py`.
