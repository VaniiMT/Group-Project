"""Script de demostración local. NO se sube al proyecto del grupo."""
import copy
from solver import solve_step_by_step
from examples import EXAMPLES


def print_board(board):
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")
        line = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                line += "| "
            line += f"{val if val != 0 else '.'} "
        print(line)


def solve_and_show(name, puzzle, mode):
    print(f"\n=== {name.upper()} en modo {mode} ===")
    print("\nPuzzle inicial:")
    print_board(puzzle)

    board = copy.deepcopy(puzzle)
    last = None
    for step in solve_step_by_step(puzzle, mode=mode):
        last = step
        if step.action == 'place':
            board[step.row][step.col] = step.value
        elif step.action == 'remove':
            board[step.row][step.col] = 0

    print("\nResultado:")
    print_board(board)
    print(f"\nEstado: {last.action}")
    print(f"Pasos (tries): {last.steps_count}")
    print(f"Retrocesos (backtracks): {last.backtracks_count}")


if __name__ == "__main__":
    solve_and_show("easy", EXAMPLES['easy'], 'classic')
    solve_and_show("hard", EXAMPLES['hard'], 'classic')
    solve_and_show("hard", EXAMPLES['hard'], 'mrv')