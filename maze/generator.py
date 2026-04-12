import random, time
from .renderer import *

class Maze:
    """
    Représente le labyrinthe entier.

    height / width : taille du labyrinthe
    entry : point d'entrée (x, y)
    exit : point de sortie (x, y)

    grid : grille 2D de Cell
    path : chemin trouvé par BFS (liste de coordonnées)

    En gros :
    c'est la structure principale qui contient tout
    """
    def __init__(self, height, width, entry, exit_):
        self.height = height
        self.width = width
        self.entry = entry
        self.exit = exit_
        self.grid = []
        self.path = []

        for y in range(height):
            row = []
            for x in range(width):
                row.append(Cell())
            self.grid.append(row)


class Cell:
    """
    Représente une case du labyrinthe.

    N E S W : murs (True = mur présent, False = ouvert)
    visited : utilisé pour DFS / BFS
    generate : utilisé pour l'affichage pendant la génération

    En gros :
    chaque case sait où sont ses murs et si elle a été visitée
    """
    def __init__(self):
        self.N = True
        self.E = True
        self.S = True
        self.W = True
        self.isbreakable = True
        self.visited = False
        self.generate = False
        self.isftwo = False


def open_wall(maze, x, y):
    """
    Ouvre un mur sur le bord du labyrinthe.

    Sert pour :
    → créer l'entrée et la sortie

    Fonctionnement :
    → regarde si la cellule est sur un bord
    → casse le mur correspondant

    Exemple :
    si y == 0 → on ouvre le mur Nord
    """
    cell = maze.grid[y][x]
    if y == 0:
        cell.N = False
    elif y == maze.height - 1:
        cell.S = False
    elif x == 0:
        cell.W = False
    elif x == maze.width - 1:
        cell.E = False

def cells_braker(current, next, direction):
    """
    Casse le mur entre 2 cellules.

    direction = "N", "E", "S", "W"

    Important :
    → casse le mur des DEUX côtés

    Exemple :
    si direction = "E"
    → current.E = False
    → next.W = False

    En gros :
    → connecte 2 cases entre elles
    """
    if not current.isbreakable or not next.isbreakable:
        return
    if direction == "E":
        current.E = False
        next.W = False
    if direction == "S":
        current.S = False
        next.N = False
    if direction == "W":
        current.W = False
        next.E = False
    if direction == "N":
        current.N = False
        next.S = False

def convert_bit(cell):
    resultat = int(cell.N) << 0 | int(cell.E) << 1 | int(cell.S) << 2 | int(cell.W) << 3
    return resultat


def convert_maze_output(maze):
    with open("outputfile.txt", "w") as f:
        for y in range(maze.height):
            for x in range(maze.width):
                f.write(f"{format(convert_bit(maze.grid[y][x]), "X")}")
            f.write("\n")


def initforty_two(maze):
    pattern = [
        "4 4 222",
        "4 4   2",
        "444 222",
        "  4 2  ",
        "  4 222",
    ]
    start_y = maze.height // 2 - len(pattern) // 2
    start_x = maze.width // 2 - len(pattern[0]) // 2

    for dy, row in enumerate(pattern):
        for dx, char in enumerate(row):
            if char != " ":
                cell = maze.grid[start_y + dy][start_x + dx]
                cell.isbreakable = False
                cell.generate = True
                cell.isftwo = True


def dfs(maze, color, type_display):
    """
    Génère un labyrinthe avec Depth First Search.

    Fonctionnement :
    → on avance en profondeur avec une stack
    → on choisit un voisin aléatoire
    → on casse le mur
    → on continue jusqu'à blocage
    → puis backtrack

    Résultat :
    → labyrinthe parfait (1 seul chemin entre 2 points)
    Bonus :
    → animation avec display_maze

    En gros :
    → simple mais très "couloir"
    """
    stack = [(0, 0)]
    maze.grid[0][0].visited = True
    while stack:
        x, y = stack[-1]
        neighbors = []

        if y > 0 and not maze.grid[y-1][x].visited and maze.grid[y-1][x].isbreakable:
            neighbors.append(("N", x, y-1))
        if x < maze.width - 1 and not maze.grid[y][x+1].visited and maze.grid[y][x+1].isbreakable:
            neighbors.append(("E", x+1, y))
        if y < maze.height - 1 and not maze.grid[y+1][x].visited and maze.grid[y+1][x].isbreakable:
            neighbors.append(("S", x, y+1))
        if x > 0 and not maze.grid[y][x-1].visited and maze.grid[y][x-1].isbreakable:
            neighbors.append(("W", x-1, y))

        if neighbors:
            direction, nx, ny = random.choice(neighbors)
            current = maze.grid[y][x]
            next_cell = maze.grid[ny][nx]
            current.generate = True
            next_cell.generate = True
            cells_braker(current, next_cell, direction)
            next_cell.visited = True
            stack.append((nx, ny))
            if type_display == "ascii":
                print("\033c")
                display_maze(maze, color)
                time.sleep(0.05)
        else:
            stack.pop()
    j, k = maze.entry
    ej, ek = maze.exit

    open_wall(maze, j, k)
    open_wall(maze, ej, ek)
    print("\033c")


def random_breaker(maze, chance=0.1):
    count = 0
    for y in range(maze.height):
        for x in range(maze.width):
            if x < maze.width - 1:
                if random.random() < chance:
                    c1, c2 = maze.grid[y][x], maze.grid[y][x+1]
                    if c1.isbreakable and c2.isbreakable:
                        cells_braker(c1, c2, "E")
                        c1.generate = c2.generate = True # Indispensable pour l'affichage
                        count += 1
            if y < maze.height - 1:
                if random.random() < chance:
                    c1, c2 = maze.grid[y][x], maze.grid[y+1][x]
                    if c1.isbreakable and c2.isbreakable:
                        cells_braker(c1, c2, "S")
                        c1.generate = c2.generate = True # Indispensable pour l'affichage
                        count += 1


def growing_tree(maze, x, y, color, type_display):
    """
    Génère un labyrinthe avec l'algo Growing Tree.

    Idée :
    → mélange entre DFS et random

    Fonctionnement :
    → liste de cellules actives
    → parfois on prend la dernière (DFS)
    → parfois une random (plus ouvert)

    Résultat :
    → labyrinthe moins rigide que DFS
    → plus naturel / varié

    Paramètre caché :
    → le ratio contrôle le style

    En gros :
    → meilleur rendu visuel que DFS pur
    """
    for row in maze.grid:
        for cell in row:
            if cell.isbreakable:
                cell.visited = False
                cell.generate = False
    cells = [(y, x)]
    maze.grid[x][y].visited = True
    maze.grid[x][y].generate = True

    while cells:
        if random.random() < 0.5:
            index = -1
        else:
            index = random.randint(0, len(cells) - 1)

        x, y = cells[index]

        neighbors = []

        if y > 0 and not maze.grid[y-1][x].visited and maze.grid[y-1][x].isbreakable:
            neighbors.append(("N", x, y-1))
        if x < maze.width - 1 and not maze.grid[y][x+1].visited and maze.grid[y][x+1].isbreakable:
            neighbors.append(("E", x+1, y))
        if y < maze.height - 1 and not maze.grid[y+1][x].visited and maze.grid[y+1][x].isbreakable:
            neighbors.append(("S", x, y+1))
        if x > 0 and not maze.grid[y][x-1].visited and maze.grid[y][x-1].isbreakable:
            neighbors.append(("W", x-1, y))

        if not neighbors:
            cells.pop(index)
            continue
        direction, nx, ny = random.choice(neighbors)

        current = maze.grid[y][x]
        next_cell = maze.grid[ny][nx]
        if current.isbreakable and next_cell.isbreakable:
            cells_braker(current, next_cell, direction)
            current.generate = True
            next_cell.generate = True
            next_cell.visited = True
            cells.append((nx, ny))
        if type_display == "ascii":
            print("\033c")
            display_maze(maze, color)
            time.sleep(0.04)
    open_wall(maze, *maze.entry)
    open_wall(maze, *maze.exit)
    print("\033c")
