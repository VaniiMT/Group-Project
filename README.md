# Sudoku Solver - Backtracking

- Lucia Martinez Hernandez
- Lucas Sanz Lopez
- Juan Ruiz Luque
- Ivan Mesonero Torreblanca

Este proyecto consiste en la creación de un resolvedor de Sudoku utilizando el algoritmo de Backtracking en Python.
El programa busca las casillas vacías del tablero e intenta rellenarlas probando números del 1 al 9. Si un número no cumple las reglas del Sudoku, el algoritmo retrocede y prueba otra opción hasta encontrar una solución válida.

Tecnologias utilizadas:
- Python
- GitHub

Como ejecutar el proyecto:
python main.py

Backtracking:
El Backtracking es una técnica basada en prueba y error. El algoritmo prueba diferentes opciones hasta encontrar una solución correcta. Si una opción no funciona, retrocede al paso anterior y prueba otra alternativa.

 Reglas del Sudoku

- Cada fila debe contener números del 1 al 9 sin repetir.
- Cada columna debe contener números del 1 al 9 sin repetir.
- Cada subcuadrícula de 3x3 debe contener números del 1 al 9 sin repetir.

 Funcionamiento del algoritmo

1. El programa busca una casilla vacía.
2. Prueba números del 1 al 9.
3. Comprueba si el número cumple las reglas.
4. Si es válido, continúa con la siguiente casilla.
5. Si no encuentra solución, retrocede y prueba otro número.

Gracias a este proyecto hemos aprendido cómo funciona el algoritmo de Backtracking y cómo puede utilizarse para resolver problemas complejos mediante prueba y error.
