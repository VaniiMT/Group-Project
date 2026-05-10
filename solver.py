class SudokuSOLVER:
    def __init__(self)
    self.steps = 0
    self.backtracks = 0

def validar(self, area, row, col, num):
    #Analizar row
    for j in range(9):  #Recorre col
        if board[row][j] == num and j != col:  # if mismo num en otra col
            return False  
    #Analizar col
    for i in range(9):
        if board[i][col] == num and i != row: 
            return False 
    #Analizar area(3x3)
    start_row = (row // 3) * 3  #inicio del bloque
    start_col = (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if area[start_row + i][start_col + j] == num:
                return False
    return True #Si todo bien procede :D


def possible_values(self, area, row, col):
    possible = []  #Guarda números válidos
    
    for num in range(1, 10): 
        if self.is_valid(area, row, col, num):
            possible.append(num)
    return possible

def find_cell_y_value(self, area):
    min_options = 10 #He puesto mayor q 9 para q no surgan errores
    best_cell = None
    best_values = None

    for i in range(9):  
        for j in range(9):  
            if area[i][j] == 0:  #Busca celdas vacios [0]

                # Calcular cuántos números pueden ir aquí
                values = [] 
                for num in range(1, 10):
                    if self.is_valid(board, i, j, num):
                        values.append(num)
            
                if len(values) < min_options:
                    min_options = len(values)  #Actualizar mínimo
                    cell = (i, j)        #Guarda posición
                    values = values      #Guarda opciones
    return cell, values 

def resolver():
    #no acabado
