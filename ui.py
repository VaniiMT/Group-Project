#Si haceis run en ui.py os muestra UI. Asegurate de pulsar limpiar cuando cambias sudoku o despues de perder. :)
#Quereis que lo personalize mas?
import tkinter as tk
from tkinter import ttk, messagebox
import time
from solver import solve_step_by_step
from examples import EXAMPLES

class SudokuUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku")
        self.root.geometry("500x650")

        #Estado del UI
        self.board = [[0]*9 for _ in range(9)]
        self.generator = None
        self.running = False
        self.start_time = None
        
        #UI
        control = ttk.Frame(root, padding="10")
        control.pack()

        #Botones de Cargar sudoku y limpiar
        ttk.Button(control, text="Easy", command=lambda: self.load(EXAMPLES["easy"])).pack(side=tk.LEFT, padx=5)
        ttk.Button(control, text="Medium", command=lambda: self.load(EXAMPLES["medium"])).pack(side=tk.LEFT, padx=5)
        ttk.Button(control, text="Hard", command=lambda: self.load(EXAMPLES["hard"])).pack(side=tk.LEFT, padx=5)
        ttk.Button(control, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=5)
        
        #Botones de elegir tipo de backtracking
        self.mode = tk.StringVar(value="classic")
        ttk.Radiobutton(control, text="Classic", variable=self.mode, value="classic").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(control, text="MRV", variable=self.mode, value="mrv").pack(side=tk.LEFT, padx=5)
        
        #Botones de control
        ttk.Button(control, text="Solve", command=self.solve).pack(side=tk.LEFT, padx=5)
        ttk.Button(control, text="Stop", command=lambda: setattr(self, "running", False)).pack(side=tk.LEFT, padx=5)
        
        #Muestra las estadisticas
        stats = ttk.Frame(root, padding="10")
        stats.pack()
        self.steps_label = ttk.Label(stats, text="Steps: 0") #Nº de pasos realizados
        self.steps_label.pack(side=tk.LEFT, padx=10)
        self.back_label = ttk.Label(stats, text="Backtracks: 0") #Nº de veces retrocede
        self.back_label.pack(side=tk.LEFT, padx=10)
        self.time_label = ttk.Label(stats, text="Time: 0.0s")
        self.time_label.pack(side=tk.LEFT, padx=10)
        
        #Ira Divina
        ira_frame = ttk.LabelFrame(root, text="Ira Divina", padding="5") #Marco
        ira_frame.pack(fill=tk.X, padx=10, pady=5) #Dimnesiones
        self.ira_bar = ttk.Progressbar(ira_frame, length=400, maximum=100) #La barra en si
        self.ira_bar.pack() #Muestra la barra
        
        #Las celdas del sudoku, cada una es un Entry que se puede editar. Se guardan en self.cells para acceder a ellas fácilmente. Cada vez que se edita una celda, se actualiza el estado del tablero en self.board.
        grid = ttk.Frame(root, padding="10") #Marco
        grid.pack() #Para mostrar
        self.cells = [] 
        for i in range(9):
            row_cells = []
            for j in range(9): #Recorre fila y columa para crear celda
                e = tk.Entry(grid, width=3, font=('Arial', 18), justify="center") #Crear
                e.grid(row=i, column=j, padx=1, pady=1) #Posicionar
                e.bind('<KeyRelease>', lambda ev, r=i, c=j: self.change(r, c)) #Cuando se edita, llama a self.change para actualizar su estado
                row_cells.append(e) #Guarda la referencia a la celda para acceder luego
            self.cells.append(row_cells) #Guarda la fila en self.cells
    
    def change(self, row, col): 
        val = self.cells[row][col].get() #Obtiene el valor de la celda editada
        self.board[row][col] = int(val) if val.isdigit() else 0 #Actualiza estado, si es digito la convierte en entero, si no lo borra (0)
    
    def load(self, puzzle): #Cargar el sudoku
        self.clear()
        for i in range(9):
            for j in range(9): #Recorre el sudoku
                if puzzle[i][j] != 0: #si es valor distinto de 0, lo muestra.
                    self.cells[i][j].insert(0, str(puzzle[i][j]))
                    self.board[i][j] = puzzle[i][j]
    
    def clear(self):
        for i in range(9):
            for j in range(9): #Reocrre
                self.cells[i][j].delete(0, tk.END) #elimia contenido en la celda
                self.board[i][j] = 0 #Reinicia el tablero entero
    
    def get_board(self): #
        b = [[0]*9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                val = self.cells[i][j].get()
                if val.isdigit():
                    b[i][j] = int(val)
        return b
    
    def solve(self): #Utiliza los metodos de solver.py
        if self.running:
            return
        self.board = self.get_board()
        self.start_time = time.time()
        self.generator = solve_step_by_step(self.board, mode=self.mode.get())
        self.running = True
        self.next_step()
        self.update_timer()
    
    def update_timer(self):  #Determina el tiempo
        if not self.running:
            return
        self.root.after(100, self.update_timer) #Cada 100ms actualiza el timer
        elapsed = time.time() - self.start_time
        self.time_label.config(text=f"Time: {elapsed:.2f}s")
        ira = min(100, (elapsed / 30) * 100) #Ira aumenta al tiempo elapsed
        self.ira_bar["value"] = ira #Actualiza barra
        
        if elapsed >= 30:
            self.running = False
            # Pantalla roja
            red = tk.Toplevel(self.root)
            red.attributes("-fullscreen", True) #Hace que ocupe toda la pantalla
            red.configure(bg='red')
            self.root.after(1000, red.destroy) #se quita la pantalla roja
            messagebox.showwarning("Ira Divina", f"Has perdido {elapsed:.2f}s")
            return
    
    def next_step(self):
        if not self.running:
            return
        try:
            step = next(self.generator)
            self.steps_label.config(text=f"Steps: {step.steps_count}")
            self.back_label.config(text=f"Backtracks: {step.backtracks_count}")
            #Cosas de solver.py. Dependiendo de la accion actualiza la celda.
            if step.action == "place":
                self.cells[step.row][step.col].delete(0, tk.END)
                self.cells[step.row][step.col].insert(0, str(step.value))
            elif step.action == "remove":
                self.cells[step.row][step.col].delete(0, tk.END)
            elif step.action == "done":
                self.running = False
                messagebox.showinfo("Sudoku resuelto!"
                                    f"Steps: {step.steps_count}"
                                    f"Backtracks: {step.backtracks_count}"
                                    f"Time: {time.time() - self.start_time:.2f}s"
                                    )
                return
            #Codigo que nunca va pasar
            elif step.action == "fail":
                self.running = False
                messagebox.showwarning("Nunca va pasar")
                return
            
            self.root.after(20, self.next_step)
        except StopIteration:
            self.running = False

root = tk.Tk()
app = SudokuUI(root)
root.mainloop()
