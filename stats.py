import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
class StatsManager:
    def __init__(self, filename='attempts.csv'):
        self.filename = filename

    def append_attempt(self, attempt: dict):
        fieldnames = ['timestamp', 'time', 'steps', 'backtracks', 'algorithm']
        try:
            with open(self.filename, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                if csvfile.tell() == 0:  # Verificar si el archivo está vacío para escribir encabezado
                    writer.writeheader()
                writer.writerow(attempt)
        except Exception as e:
            print(f"Error escribiendo en {self.filename}: {e}")

    def read_attempts(self):
        attempts = []
        try:
            with open(self.filename, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    attempts.append(row)
        except FileNotFoundError:
            print(f"{self.filename} no encontrado. Devolviendo lista vacía.")
        except Exception as e:
            print(f"Error leyendo de {self.filename}: {e}")
        return attempts
    def show_graphs(self):
        attempts = self.read_attempts()
        if not attempts:
            print("Sin intentos para mostrar.")
            return

        times = [float(attempt['time']) for attempt in attempts]
        steps = [int(attempt['steps']) for attempt in attempts]
        backtracks = [int(attempt['backtracks']) for attempt in attempts]

        # Crear ventana Tkinter
        root = tk.Toplevel()
        root.title("Estadísticas de Intentos")

        # Crear subtramas
        fig, axs = plt.subplots(2, 2, figsize=(10, 8))

        # Tiempo por intento
        axs[0, 0].plot(times, marker='o')
        axs[0, 0].set_title('Tiempo por intento')
        axs[0, 0].set_xlabel('Intento')
        axs[0, 0].set_ylabel('Tiempo (s)')

        
        axs[0, 1].plot(steps, marker='o', color='orange')
        axs[0, 1].set_title('Pasos por intento')
        axs[0, 1].set_xlabel('Intento')
        axs[0, 1].set_ylabel('Pasos')

        
        axs[1, 0].plot(backtracks, marker='o', color='red')
        axs[1, 0].set_title('Retrocesos por intento')
        axs[1, 0].set_xlabel('Intento')
        axs[1, 0].set_ylabel('Retrocesos')

        # Comparación de algoritmos
        mrv_times = [float(attempt['time']) for attempt in attempts if attempt['algorithm'] == 'mrv']
        classic_times = [float(attempt['time']) for attempt in attempts if attempt['algorithm'] == 'classic']
        
        # Grafico de lineas separado en clasico y mrv
        if mrv_times and classic_times:
            axs[1, 1].plot(mrv_times, marker='o', color='blue', label='mrv')
            axs[1, 1].plot(classic_times, marker='s', color='orange', label='clásico')
            axs[1, 1].set_title(f'Comparación de Tiempo: mrv vs clásico\n(mrv: {len(mrv_times)}, clásico: {len(classic_times)})')
            axs[1, 1].set_ylabel('Tiempo (s)')
            axs[1, 1].legend()
            mrv_avg = sum(mrv_times) / len(mrv_times)
            classic_avg = sum(classic_times) / len(classic_times)
            axs[1, 1].text(0.5, 0.95, f'promedio mrv: {mrv_avg:.2f}s\npromedio clásico: {classic_avg:.2f}s', 
                          transform=axs[1, 1].transAxes, verticalalignment='top', horizontalalignment='center',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        elif mrv_times:
            axs[1, 1].plot(mrv_times, marker='o', color='blue')
            axs[1, 1].set_title(f'Solo hay datos de mrv ({len(mrv_times)} intentos)')
            axs[1, 1].set_ylabel('Tiempo (s)')
        elif classic_times:
            axs[1, 1].plot(classic_times, marker='o', color='orange')
            axs[1, 1].set_title(f'Solo hay datos de clásico ({len(classic_times)} intentos)')
            axs[1, 1].set_ylabel('Tiempo (s)')
        else:
            axs[1, 1].text(0.5, 0.5, 'No hay datos que comparar', 
                          horizontalalignment='center', verticalalignment='center',
                          transform=axs[1, 1].transAxes)
        
        plt.tight_layout()

        # Insertar el gráfico en la ventana Tkinter
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        
        root.wait_window(root)


stats = StatsManager()
stats.show_graphs()