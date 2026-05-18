import signal
import tkinter as tk
from tkinter import ttk, messagebox
import time
import matplotlib.pyplot as plt
from solver import solve_step_by_step
from examples import EXAMPLES
from stats import StatsManager


# ===== Paleta y tipografía =====
BG_APP = "#F5F5F7"             # fondo general de la ventana
BG_BOARD_BORDER = "#2D3748"    # borde grueso del tablero y separación entre bloques
BG_CELL_EDITABLE = "#FFFFFF"   # celda vacía / editable
BG_CELL_ORIGINAL = "#E6ECF5"   # celda cargada desde un ejemplo (pista fija)
BG_CELL_PLACED = "#DCFCE7"     # celda rellenada por el solver (verde suave)
FG_ORIGINAL = "#1A1A1A"        # texto de pista fija
FG_EDITABLE = "#2563EB"        # texto introducido por el usuario (azul)
FG_TITLE = "#1A1A1A"
FG_SUBTITLE = "#6B7280"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUBTITLE = ("Segoe UI", 10)
FONT_SECTION = ("Segoe UI", 10, "bold")
FONT_CELL = ("Segoe UI", 20, "bold")
FONT_STATUS = ("Segoe UI", 12)


class SudokuUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.geometry("600x820")
        self.root.minsize(560, 780)
        self.root.configure(bg=BG_APP)

        # Estado del UI
        self.board = [[0]*9 for _ in range(9)]
        self.original = [[False]*9 for _ in range(9)]   # marca pistas fijas
        self.generator = None
        self.running = False
        self.start_time = None
        self.stats_manager = StatsManager()
        # IDs de callbacks pendientes — se cancelan al parar/reiniciar para
        # evitar que un timer antiguo siga disparándose tras 'done'/'stop'.
        self._timer_id = None
        self._step_id = None

        self._setup_styles()
        self._build_header(root)
        self._build_board(root)
        self._build_status(root)
        self._build_ira(root)
        self._build_examples_controls(root)
        self._build_actions(root)

    # ===== Construcción visual =====

    def _setup_styles(self):
        """Configura el tema ttk y estilos personalizados para la app."""
        style = ttk.Style()
        # 'clam' está disponible en la mayoría de sistemas y da un look más limpio
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('App.TFrame', background=BG_APP)
        style.configure('App.TLabel', background=BG_APP, font=FONT_STATUS)
        style.configure('Title.TLabel', background=BG_APP, font=FONT_TITLE, foreground=FG_TITLE)
        style.configure('Subtitle.TLabel', background=BG_APP, font=FONT_SUBTITLE, foreground=FG_SUBTITLE)
        style.configure('Section.TLabelframe', background=BG_APP)
        style.configure('Section.TLabelframe.Label', background=BG_APP, font=FONT_SECTION)
        style.configure('TButton', padding=6)
        style.configure('TRadiobutton', background=BG_APP)

    def _build_header(self, parent):
        header = ttk.Frame(parent, style='App.TFrame', padding=(10, 14, 10, 4))
        header.pack(fill=tk.X)
        ttk.Label(header, text="Sudoku Solver", style='Title.TLabel').pack()
        ttk.Label(header, text="Backtracking clásico y heurística MRV",
                  style='Subtitle.TLabel').pack()

    def _build_board(self, parent):
        """Construye un tablero 9x9 con borde grueso entre bloques 3x3."""
        # Marco exterior oscuro: actúa como borde del tablero y separación entre bloques
        outer = tk.Frame(parent, bg=BG_BOARD_BORDER, padx=3, pady=3)
        outer.pack(padx=20, pady=10)

        self.cells = [[None]*9 for _ in range(9)]
        for br in range(3):
            for bc in range(3):
                block = tk.Frame(outer, bg=BG_BOARD_BORDER)
                # padx/pady=2 entre bloques crea la separación gruesa visible
                block.grid(row=br, column=bc, padx=2, pady=2)
                for r in range(3):
                    for c in range(3):
                        i, j = br*3 + r, bc*3 + c
                        cell = tk.Entry(
                            block, width=2,
                            font=FONT_CELL, justify="center",
                            bg=BG_CELL_EDITABLE, fg=FG_EDITABLE,
                            disabledbackground=BG_CELL_ORIGINAL,
                            disabledforeground=FG_ORIGINAL,
                            bd=0, relief=tk.FLAT, highlightthickness=0,
                        )
                        # padx/pady=1 entre celdas crea la separación fina visible
                        cell.grid(row=r, column=c, padx=1, pady=1, ipady=6)
                        self.cells[i][j] = cell

    def _build_status(self, parent):
        status = ttk.LabelFrame(parent, text="Estado",
                                style='Section.TLabelframe', padding=(10, 6))
        status.pack(fill=tk.X, padx=20, pady=(4, 4))
        self.steps_label = ttk.Label(status, text="Pasos: 0", style='App.TLabel')
        self.steps_label.pack(side=tk.LEFT, padx=12)
        self.back_label = ttk.Label(status, text="Retrocesos: 0", style='App.TLabel')
        self.back_label.pack(side=tk.LEFT, padx=12)
        self.time_label = ttk.Label(status, text="Tiempo: 0.00s", style='App.TLabel')
        self.time_label.pack(side=tk.LEFT, padx=12)

    def _build_ira(self, parent):
        ira_frame = ttk.LabelFrame(parent, text="Ira Divina",
                                   style='Section.TLabelframe', padding=(10, 6))
        ira_frame.pack(fill=tk.X, padx=20, pady=(0, 6))
        self.ira_bar = ttk.Progressbar(ira_frame, length=500, maximum=100)
        self.ira_bar.pack(fill=tk.X)

    def _build_examples_controls(self, parent):
        ex = ttk.LabelFrame(parent, text="Ejemplos y modo",
                            style='Section.TLabelframe', padding=(10, 6))
        ex.pack(fill=tk.X, padx=20, pady=(0, 4))
        ttk.Button(ex, text="Fácil",
                   command=lambda: self.load(EXAMPLES["easy"])).pack(side=tk.LEFT, padx=4)
        ttk.Button(ex, text="Medio",
                   command=lambda: self.load(EXAMPLES["medium"])).pack(side=tk.LEFT, padx=4)
        ttk.Button(ex, text="Difícil",
                   command=lambda: self.load(EXAMPLES["hard"])).pack(side=tk.LEFT, padx=4)
        ttk.Separator(ex, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=12)
        self.mode = tk.StringVar(value="classic")
        ttk.Radiobutton(ex, text="Clásico", variable=self.mode,
                        value="classic").pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(ex, text="MRV", variable=self.mode,
                        value="mrv").pack(side=tk.LEFT, padx=4)

    def _build_actions(self, parent):
        actions = ttk.LabelFrame(parent, text="Acciones",
                                 style='Section.TLabelframe', padding=(10, 6))
        actions.pack(fill=tk.X, padx=20, pady=(0, 14))
        ttk.Button(actions, text="Resolver", command=self.solve).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Detener", command=self._stop).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Limpiar", command=self.clear).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Estadísticas",
                   command=self.show_stats).pack(side=tk.RIGHT, padx=4)
    
    def load(self, puzzle): #Cargar el sudoku
        self.clear()
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    self._set_original(i, j, puzzle[i][j])

    def _set_original(self, i, j, val):
        """Marca una celda como pista fija: la deshabilita para que el usuario
        no la edite y queda con un estilo distinto al de las celdas editables."""
        cell = self.cells[i][j]
        cell.config(state='normal')
        cell.delete(0, tk.END)
        cell.insert(0, str(val))
        cell.config(state='disabled')
        self.original[i][j] = True
        self.board[i][j] = val

    def clear(self):
        self._stop()
        for i in range(9):
            for j in range(9):
                cell = self.cells[i][j]
                # Habilitar antes de borrar (un Entry disabled no acepta delete)
                cell.config(state='normal')
                cell.delete(0, tk.END)
                cell.config(bg=BG_CELL_EDITABLE, fg=FG_EDITABLE)
                self.original[i][j] = False
                self.board[i][j] = 0

    def _stop(self):
        """Detiene la animación y cancela cualquier callback pendiente."""
        self.running = False
        if self._timer_id is not None:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        if self._step_id is not None:
            self.root.after_cancel(self._step_id)
            self._step_id = None
    
    def get_board(self):
        """Lee las 81 celdas. Vacío -> 0; dígito 1-9 -> int.
        Cualquier otro contenido lanza ValueError con la posición 1-indexada."""
        b = [[0]*9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                val = self.cells[i][j].get().strip()
                if val == "":
                    continue
                if not (val.isdigit() and 1 <= int(val) <= 9):
                    raise ValueError(
                        f"Celda ({i + 1}, {j + 1}) contiene '{val}'. "
                        "Solo se permiten dígitos del 1 al 9 o vacío."
                    )
                b[i][j] = int(val)
        return b

    def solve(self): #Utiliza los metodos de solver.py
        if self.running:
            return
        # Cancelar cualquier timer residual de una ejecución previa
        self._stop()
        try:
            self.board = self.get_board()
            self.generator = solve_step_by_step(self.board, mode=self.mode.get())
        except ValueError as e:
            messagebox.showerror("Tablero inválido", str(e))
            return
        self.start_time = time.time()
        self.running = True
        self.next_step()
        self.update_timer()

    def update_timer(self):  #Determina el tiempo
        if not self.running:
            return
        self._timer_id = self.root.after(100, self.update_timer) #Cada 100ms actualiza el timer
        elapsed = time.time() - self.start_time
        self.time_label.config(text=f"Tiempo: {elapsed:.2f}s")
        ira = min(100, (elapsed / 30) * 100) #Ira aumenta al tiempo elapsed
        self.ira_bar["value"] = ira #Actualiza barra

        if elapsed >= 30:
            self._stop()
            self._show_ira_divina(elapsed)
            return

    def next_step(self):
        if not self.running:
            return
        try:
            step = next(self.generator)
            self.steps_label.config(text=f"Pasos: {step.steps_count}")
            self.back_label.config(text=f"Retrocesos: {step.backtracks_count}")
            cell = self.cells[step.row][step.col]
            if step.action == "place":
                cell.delete(0, tk.END)
                cell.insert(0, str(step.value))
                cell.config(bg=BG_CELL_PLACED)
            elif step.action == "remove":
                cell.delete(0, tk.END)
                cell.config(bg=BG_CELL_EDITABLE)
            elif step.action == "done":
                elapsed_time = time.time() - self.start_time
                self._stop()
                # Record the attempt in stats
                self.stats_manager.append_attempt({
                    "timestamp": time.time(),
                    "time": elapsed_time,
                    "steps": step.steps_count,
                    "backtracks": step.backtracks_count,
                    "algorithm": self.mode.get()
                })
                messagebox.showinfo("Sudoku resuelto",
                                    f"Pasos: {step.steps_count}\n"
                                    f"Retrocesos: {step.backtracks_count}\n"
                                    f"Tiempo: {elapsed_time:.2f}s")
                return
            #Codigo que nunca va pasar
            elif step.action == "fail":
                self._stop()
                messagebox.showwarning("Nunca va pasar")
                return

            self._step_id = self.root.after(20, self.next_step)
        except StopIteration:
            self._stop()

    def _show_ira_divina(self, elapsed):
        """Pantalla roja con cierre manual (Escape, clic o botón) y
        cierre automático tras 1s. Diseñada para no atrapar al usuario."""
        red = tk.Toplevel(self.root)
        red.attributes("-fullscreen", True)
        red.configure(bg='red')

        def close(_event=None):
            if red.winfo_exists():
                red.destroy()

        # Botón visible centrado para cerrar manualmente
        tk.Button(red, text="Cerrar (Esc)", font=('Arial', 20),
                  command=close).place(relx=0.5, rely=0.5, anchor='center')

        # Atajos: Escape o clic en cualquier sitio
        red.bind('<Escape>', close)
        red.bind('<Button-1>', close)
        red.focus_set()

        # Cierre automático tras 1s (seguro si el usuario ya cerró)
        self.root.after(1000, close)

        messagebox.showwarning("Ira Divina", f"Has perdido {elapsed:.2f}s")

    def show_stats(self):
        self.stats_manager.show_graphs()

    def close(self):
        """Cierre limpio: para timers, libera figuras matplotlib y destruye root.
        Seguro de llamar varias veces (idempotente)."""
        self._stop()
        # Red de seguridad: cualquier figura que aún esté registrada en pyplot
        plt.close('all')
        try:
            self.root.destroy()
        except tk.TclError:
            pass


def main():
    root = tk.Tk()
    app = SudokuUI(root)

    # Cerrar limpiamente al pulsar la X de la ventana principal
    root.protocol("WM_DELETE_WINDOW", app.close)

    # Permitir Ctrl+C: Tk bloquea en código C y no procesa señales hasta que
    # vuelve el control a Python. Un 'after' periódico despierta el intérprete,
    # y el handler de SIGINT programa el cierre en el hilo de Tk.
    def _keepalive():
        root.after(200, _keepalive)
    root.after(200, _keepalive)

    def _on_sigint(_signum, _frame):
        root.after(0, app.close)
    signal.signal(signal.SIGINT, _on_sigint)

    root.mainloop()


if __name__ == "__main__":
    main()
