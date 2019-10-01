import pygame
from pygame.locals import QUIT, RLEACCEL, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_KP0, K_KP1, K_KP2, K_KP3, K_KP4, K_KP5, K_KP6, K_KP7, K_KP8, K_KP9, K_BACKSPACE
pygame.init()
pygame.font.init()

from os import path
""" Variables """
# Tamaño de la ventana
Width  = 550
Height = 600

# Creamos la ventana
win = pygame.display.set_mode((Width,Height))

# Se le pone un titulo a la ventana 
pygame.display.set_caption("Sudoku-Backtracking")

# Se carga el tablero del sudoku
board = pygame.image.load('Sudoku_board.jpg')

# Creamos una base de timepo
clock = pygame.time.Clock()

# Lista de números que se quieren colocar
numbers = []

# Posicion del Foco (azul)
posicionx = 0
posiciony = 0
keycooldown = 4
keyavaliable = True

class Number(object):
    def __init__(self, number, x, y, font = pygame.font.SysFont('Arial', 50, True)):
        self.number = number
        self.x = x
        self.y = y
        self.font = font

    def draw(self, win):
        if self.number != 0:
            win.blit( self.font.render(str(self.number), True, (0, 0, 0) ), (self.x , self.y ))
        else:
            win.blit( self.font.render(" ", True, (0, 0, 0) ), (self.x , self.y ))

class Button(object):
    def __init__(self, color, x, y, width, height, text = ''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.thickness = 2

    def draw(self, win, outline = None):
        if outline:
            pygame.draw.rect(win, outline, (self.x - self.thickness, self.y - self.thickness, self.width + 2 * self.thickness, self.height + 2 * self.thickness), 0)
        
        pygame.draw.rect(win, self.color ,(self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('Arial', 30)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (self.x + (self.width / 2 - text.get_width() / 2) - 4, self.y + (self.height / 2 - text.get_height() / 2)))
    
    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

# Creamos los botones que necesitaremos
Button_Solve = Button((166, 168, 173), 12, 550, 130, 40, ' Resolver')
Button_clear_sudoku = Button((166, 168, 173), 160, 550, 160, 40, ' Borrar Todo')

# Dibujamos un cuadro azul sobre el cuadro en el cual queremos colocar un número
def drawfocus(win,x, y):
    pygame.draw.rect(win, (18, 169, 232), (x, y, 50, 50), 1)

def print_actual_sudoku(sudoku, Sudoku_draw):
    sudoku_n = []
    sudoku1 = []
    sudoku2 = []
    s_sudoku = []
    s_sudoku1 = []
    s_sudoku2 = []

    for i in range(len(sudoku)):
        aux3 = []
        for j in range(len(sudoku[0])):
            aux3.append(sudoku[i][j])
        sudoku_n.append(aux3)
    del aux3 

    for i in  range(len(sudoku_n)):
        sudoku_n[i].insert(3,"  |  ")
        sudoku_n[i].insert(7,"  | ")
        sudoku_n[i].insert(11,"\n")
    
    for i in range(len(sudoku_n)):
        for j in range(len(sudoku_n[0])):
            sudoku1.append(sudoku_n[i][j])


    sudoku1.insert(36, "-----+-------+-----")
    sudoku1.insert(37,"\n")
    sudoku1.insert(74, "-----+-------+-----")
    sudoku1.insert(75,'\n')

    for i in range(len(sudoku1)):
        sudoku1[i] = str(sudoku1[i])
    
    aux2 = []
    # representamos igual que el primer sudoku
    for i in range(len(Sudoku_draw)):
        aux = []
        for j in range(len(Sudoku_draw[0])):
            aux.append(str(Sudoku_draw[i][j].number))
        aux2.append(aux)
    del aux

    for i in  range(len(Sudoku_draw)):
        aux2[i].insert(3,"  |  ")
        aux2[i].insert(7,"  | ")
        aux2[i].insert(11,"\n")
    
    for i in range(len(Sudoku_draw)):
        for j in range(len(aux2[0])):
            sudoku2.append(aux2[i][j])
    del aux2

    sudoku2.insert(36, "-----+-------+-----")
    sudoku2.insert(37,"\n")
    sudoku2.insert(74, "-----+-------+-----")
    sudoku2.insert(75,'\n')

    s_sudoku1 = "".join(sudoku1)
    s_sudoku2 = "".join(sudoku2)
    s_sudoku1 = s_sudoku1.split('\n')
    s_sudoku2 = s_sudoku2.split('\n')

    for i in range(12):
        s_sudoku.append(s_sudoku1[i] + "                     " + s_sudoku2[i] + '\n')       

    # Necesito imprimir ambos al tiempo en la misma linea 
    print("".join(s_sudoku))

def find_empty(sudoku, sudoku_draw):
    for i in range(len(sudoku)):
        for j in range(len(sudoku[0])):
            if sudoku[i][j] == 0:
                return (i, j)
    return None

def valid(sudoku, sudoku_draw, num, pos):
     # Miramos las filas
    for i in range(len(sudoku[0])):
         if sudoku[pos[0]][i] == num and pos[1] != i:
             return False

    # Miramos las columnas
    for i in range(len(sudoku)):
        if sudoku[i][pos[1]] == num and pos[0] != i:
            return False
    
    # Miramos los cuadrantes
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if sudoku[i][j] == num and (i,j) != pos:
                return False

    return True

def solve_sudoku(sudoku, sudoku_draw):
    empty = find_empty(sudoku, sudoku_draw)
    if not(empty):
        return True
    else:
        row, col = empty
    
    for i in range(1,10):
        if valid(sudoku, sudoku_draw, i, (row, col)):
            sudoku[row][col] = i
            sudoku_draw[row][col] = Number(i, 12 + col * 60, 12 + row * 60)
            redrawGameWindow()
            
            if solve_sudoku(sudoku, sudoku_draw):
                return True
                
            sudoku[row][col] = 0
            sudoku_draw[row][col] = Number(0, 12 + col * 60, 12 + row * 60)
            redrawGameWindow()
    
    return False

def clear_sudoku(sudoku, sudoku_draw):
    for i in range(len(sudoku)):
        for j in range(len(sudoku[0])):
            sudoku[i][j] = 0
            sudoku_draw[i][j] = Number(0, 12 + 0 * 60, 12 + 0 * 60, Sudoku_draw[posicionx][posiciony].font)
    print_actual_sudoku(sudoku, sudoku_draw)

def redrawGameWindow():
    win.blit(board, (5,5))
    drawfocus(win, 12 + posicionx * 60, 12 + posiciony * 60)

    for i in range(9):
        for j in range(9):
            aux = Sudoku_draw[i][j] 
            aux.draw(win)

    Button_Solve.draw(win, (255, 255, 255))
    Button_clear_sudoku.draw(win, (255, 255, 255))

    win.blit(tiempo.render(f"time:{horas}:{minutos}:{segundos}", True, (255, 255, 255)), (400, 555))

    pygame.display.update()

# Creamos el tablero de sudoku
Sudoku = []
Sudoku_draw = []
available_numbers = []
for _ in range(9):
    aux = []
    aux2 = []
    for __ in range(9):
        aux.append(0)
        aux2.append(Number(0, 12 + __ * 60 , 12 + _ * 60,pygame.font.SysFont('Arial', 50, True)))
    Sudoku.append(aux)
    Sudoku_draw.append(aux2)
del aux, aux2

#Cargamos un sudoku inicial:
for _ in range(1):
    Sudoku[0][0] = 5
    Sudoku_draw[0][0] = Number(5, 12 + 0 * 60, 12 + 0 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[0][1] = 3
    Sudoku_draw[0][1] = Number(3, 12 + 1 * 60, 12 + 0 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[0][4] = 7
    Sudoku_draw[0][4] = Number(7, 12 + 4 * 60, 12 + 0 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[1][0] = 6
    Sudoku_draw[1][0] = Number(6, 12 + 0 * 60, 12 + 1 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[1][3] = 1
    Sudoku_draw[1][3] = Number(1, 12 + 3 * 60, 12 + 1 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[1][4] = 9
    Sudoku_draw[1][4] = Number(9, 12 + 4 * 60, 12 + 1 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[1][5] = 5
    Sudoku_draw[1][5] = Number(5, 12 + 5 * 60, 12 + 1 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[2][1] = 9
    Sudoku_draw[2][1] = Number(9, 12 + 1 * 60, 12 + 2 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[2][2] = 8
    Sudoku_draw[2][2] = Number(8, 12 + 2 * 60, 12 + 2 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[2][7] = 6
    Sudoku_draw[2][7] = Number(6, 12 + 7 * 60, 12 + 2 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[3][0] = 8
    Sudoku_draw[3][0] = Number(8, 12 + 0 * 60, 12 + 3 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[3][4] = 6
    Sudoku_draw[3][4] = Number(6, 12 + 4 * 60, 12 + 3 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[3][8] = 3
    Sudoku_draw[3][8] = Number(3, 12 + 8 * 60, 12 + 3 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[4][0] = 4
    Sudoku_draw[4][0] = Number(4, 12 + 0 * 60, 12 + 4 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[4][3] = 8
    Sudoku_draw[4][3] = Number(8, 12 + 3 * 60, 12 + 4 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[4][5] = 3
    Sudoku_draw[4][5] = Number(3, 12 + 5 * 60, 12 + 4 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[4][8] = 1
    Sudoku_draw[4][8] = Number(1, 12 + 8 * 60, 12 + 4 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[5][0] = 7
    Sudoku_draw[5][0] = Number(7, 12 + 0 * 60, 12 + 5 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[5][4] = 2
    Sudoku_draw[5][4] = Number(2, 12 + 4 * 60, 12 + 5 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[5][8] = 6
    Sudoku_draw[5][8] = Number(6, 12 + 8 * 60, 12 + 5 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[6][1] = 6
    Sudoku_draw[6][1] = Number(6, 12 + 1 * 60, 12 + 6 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[6][6] = 2
    Sudoku_draw[6][6] = Number(2, 12 + 6 * 60, 12 + 6 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[6][7] = 8
    Sudoku_draw[6][7] = Number(8, 12 + 7 * 60, 12 + 6 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[7][3] = 4
    Sudoku_draw[7][3] = Number(4, 12 + 3 * 60, 12 + 7 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[7][4] = 1
    Sudoku_draw[7][4] = Number(1, 12 + 4 * 60, 12 + 7 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[7][5] = 9
    Sudoku_draw[7][5] = Number(9, 12 + 5 * 60, 12 + 7 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[7][8] = 5
    Sudoku_draw[7][8] = Number(5, 12 + 8 * 60, 12 + 7 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[8][4] = 8
    Sudoku_draw[8][4] = Number(8, 12 + 4 * 60, 12 + 8 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[8][7] = 7
    Sudoku_draw[8][7] = Number(7, 12 + 7 * 60, 12 + 8 * 60, Sudoku_draw[posicionx][posiciony].font)
    Sudoku[8][8] = 9
    Sudoku_draw[8][8] = Number(9, 12 + 8 * 60, 12 + 8 * 60, Sudoku_draw[posicionx][posiciony].font)
    print_actual_sudoku(Sudoku, Sudoku_draw)

gaming = True

#Creamos una nueva fuente para colocar el tiempo
timer = pygame.time.set_timer(pygame.USEREVENT, 1000)
segundos, minutos, horas = 0, 0, 0
tiempo = pygame.font.SysFont('Arial', 25, True)

while gaming:
    win.fill((0, 70, 94))
    clock.tick(30)
    for eventos in pygame.event.get():
        pos = pygame.mouse.get_pos()        
        if eventos.type == QUIT:
            gaming = False
        
        # Chequeamos el timer
        if eventos.type == pygame.USEREVENT:
            segundos += 1
            if segundos == 60:
                minutos += 1
                segundos = 0
            if minutos == 60:
                horas += 1
                minutos = 0
            
        # Chequeamos si se clickeo el boton
        if eventos.type == pygame.MOUSEBUTTONDOWN:
            if Button_Solve.isOver(pos):
                solve_sudoku(Sudoku, Sudoku_draw)
            if Button_clear_sudoku.isOver(pos):
                clear_sudoku(Sudoku, Sudoku_draw)
                segundos, minutos, horas = 0, 0, 0

        if eventos.type == pygame.MOUSEMOTION:
            Button_Solve.color = (255, 168, 173) if Button_Solve.isOver(pos) else (166, 168, 173) 
            Button_clear_sudoku.color = (255, 168, 173) if Button_clear_sudoku.isOver(pos) else (166, 168, 173)


    #### Validamos si se está capturando una tecla

    # Evitamos rebotes de tecla
    if keyavaliable == False and keycooldown > 0:
        keycooldown -= 1
        keyavaliable = True if keycooldown == 0 else False

    keys_pressed = pygame.key.get_pressed()

    """ Eventos de teclado """
    # Evaluamos que tecla está epresionando
    if keys_pressed[K_UP] and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        if posiciony > 0:
            posiciony -= 1
    elif keys_pressed[K_DOWN] and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        if posiciony < 8:
            posiciony += 1
    elif keys_pressed[K_LEFT] and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        if posicionx > 0:
            posicionx -= 1
    elif keys_pressed[K_RIGHT] and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        if posicionx < 8:
            posicionx += 1
    elif (keys_pressed[K_1] or keys_pressed[K_KP1]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 1
        Sudoku_draw[posiciony][posicionx] = Number(1, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)
    elif (keys_pressed[K_2] or keys_pressed[K_KP2]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 2
        Sudoku_draw[posiciony][posicionx] = Number(2, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)
    elif (keys_pressed[K_3] or keys_pressed[K_KP3]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 3
        Sudoku_draw[posiciony][posicionx] = Number(3, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)
    elif (keys_pressed[K_4] or keys_pressed[K_KP4]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 4
        Sudoku_draw[posiciony][posicionx] = Number(4, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)
    elif (keys_pressed[K_5] or keys_pressed[K_KP5]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 5
        Sudoku_draw[posiciony][posicionx] = Number(5, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)       
    elif (keys_pressed[K_6] or keys_pressed[K_KP6]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 6
        Sudoku_draw[posiciony][posicionx] = Number(6, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)    
    elif (keys_pressed[K_7] or keys_pressed[K_KP7]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 7
        Sudoku_draw[posiciony][posicionx] = Number(7, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)    
    elif (keys_pressed[K_8] or keys_pressed[K_KP8]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 8
        Sudoku_draw[posiciony][posicionx] = Number(8, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)   
    elif (keys_pressed[K_9] or keys_pressed[K_KP9]) and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 9
        Sudoku_draw[posiciony][posicionx] = Number(9, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)    
    elif keys_pressed[K_BACKSPACE]  and keyavaliable:
        keyavaliable = False
        keycooldown = 4
        Sudoku[posiciony][posicionx] = 0
        Sudoku_draw[posiciony][posicionx] = Number(0, 12 + posicionx * 60, 12 + posiciony * 60, Sudoku_draw[posicionx][posiciony].font)
        print_actual_sudoku(Sudoku, Sudoku_draw)
           
    redrawGameWindow()

pygame.quit()