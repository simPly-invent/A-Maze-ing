import random
import time
import os

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
        self.visited = False
        self.generate = False


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


def display_maze(maze):
    """
    Affiche le labyrinthe dans le terminal.

    Gère :
    → les murs (│ ─ ┼ etc)
    → l'entrée (o jaune)
    → la sortie (o violet)
    → le chemin BFS (.)

    Bonus :
    → si generate == False → case pas encore générée

    En gros :
    → c'est uniquement de l'affichage, aucune logique de labyrinthe
    """
    height = maze.height
    width = maze.width

    print("┌" + "───┬" * (width - 1) + "───┐")

    for y in range(height):
        line1 = "│"
        line2 = "├"

        for x in range(width):
            cell = maze.grid[y][x]
            if not cell.generate:
                line1 += "   "
                line1 += "│"
                continue
            if (x, y) == maze.entry:
                line1 += " \033[33mo\033[0m "
            elif (x, y) == maze.exit:
                line1 += "\033[35m o \033[0m"
            elif (x, y) in maze.path:
                line1 += " . "
            else:
                line1 += "   "

            if cell.E:
                line1 += "│"
            else:
                line1 += " "

            if cell.S:
                line2 += "───┼"
            else:
                line2 += "   ┼"

        line1 = line1[:-1] + "│"
        line2 = line2[:-1] + "┤"

        print(line1)

        if y < height - 1:
            print(line2)

    print("└" + "───┴" * (width - 1) + "───┘")


def parser_conf(data):
    """
    Parse le fichier config.txt.

    Format attendu :
    KEY=VALUE

    Ignore :
    → lignes vides
    → commentaires (#)

    Retour :
    → dictionnaire avec les configs

    En gros :
    → permet de config le labyrinthe facilement
    """
    config_dico = {}
    for line in data.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config_dico[key] = value
    return config_dico


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


def add_loops(maze, chance=0.1):
    """
    Ajoute des boucles dans le labyrinthe.

    Pourquoi :
    → DFS / Growing Tree crée un labyrinthe parfait (1 seul chemin)
    → ici on casse des murs en plus pour créer plusieurs solutions

    chance :
    → probabilité de casser un mur (ex: 0.6 = beaucoup de loops)

    En gros :
    → rend le labyrinthe moins "rigide"
    """
    for y in range(maze.height):
        for x in range(maze.width):

            directions = ["N", "E", "S", "W"]
            direction = random.choice(directions)

            nx, ny = x, y

            if direction == "N" and y > 0:
                ny -= 1
            elif direction == "S" and y < maze.height - 1:
                ny += 1
            elif direction == "E" and x < maze.width - 1:
                nx += 1
            elif direction == "W" and x > 0:
                nx -= 1
            else:
                continue

            if random.random() < chance:
                cells_braker(maze.grid[y][x], maze.grid[ny][nx], direction)

def no_wall(direction, maze, coordinate):
    """
    Trouve le PLUS COURT chemin entre entrée et sortie.

    Algorithme :
    → parcours en largeur (queue FIFO)

    Étapes :
    1. on part de l'entrée
    2. on explore tous les voisins accessibles
    3. on stocke les parents (pour reconstruire le chemin)
    4. quand on atteint la sortie → stop
    5. on remonte le chemin avec parent

    Résultat :
    → maze.path contient le chemin final

    Important :
    → marche même avec des boucles
    → garantit le plus court chemin
    """
    wall = False
    x, y = coordinate
    if direction == "N" and not maze.grid[y][x].N:
        wall = True
    elif direction == "E" and not maze.grid[y][x].E:
        wall = True
    elif direction == "S" and not maze.grid[y][x].S:
        wall = True
    elif direction == "W" and not maze.grid[y][x].W:
        wall = True
    return wall


def bfs(maze):
    """
    Trouve le PLUS COURT chemin entre entrée et sortie.

    Algorithme :
    → parcours en largeur (queue FIFO)

    Étapes :
    1. on part de l'entrée
    2. on explore tous les voisins accessibles
    3. on stocke les parents (pour reconstruire le chemin)
    4. quand on atteint la sortie → stop
    5. on remonte le chemin avec parent

    Résultat :
    → maze.path contient le chemin final

    Important :
    → marche même avec des boucles
    → garantit le plus court chemin
    """
    maze.path = []
    x, y = maze.entry
    cells = [(x, y)]
    parent = {}
    for row in maze.grid:
        for cell in row:
            cell.visited = False
    maze.grid[y][x].visited = True
    while (cells):
        x, y = cells.pop(0)
        if (x, y) == maze.exit:
            print("target find")
            break
        neighbors = []

        if y > 0 and not maze.grid[y-1][x].visited:
            neighbors.append(("N", x, y-1))

        if x < maze.width - 1 and not maze.grid[y][x+1].visited:
            neighbors.append(("E", x+1, y))

        if y < maze.height - 1 and not maze.grid[y+1][x].visited:
            neighbors.append(("S", x, y+1))

        if x > 0 and not maze.grid[y][x-1].visited:
            neighbors.append(("W", x-1, y))

        for neighbor in neighbors:
            direction, nx, ny = neighbor
            coordinate = x, y
            good_way = no_wall(direction, maze, coordinate)
            if good_way and not maze.grid[ny][nx].visited:
                maze.grid[ny][nx].visited = True
                parent[(nx, ny)] = (x, y)
                cells.append((nx, ny))
    position = maze.exit
    while position in parent:
        maze.path.append(position)
        position = parent[position]
    maze.path.append(maze.entry)
    maze.path.reverse()
    display_maze(maze)


def dfs(maze):
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

        if y > 0 and not maze.grid[y-1][x].visited:
            neighbors.append(("N", x, y-1))

        if x < maze.width - 1 and not maze.grid[y][x+1].visited:
            neighbors.append(("E", x+1, y))

        if y < maze.height - 1 and not maze.grid[y+1][x].visited:
            neighbors.append(("S", x, y+1))

        if x > 0 and not maze.grid[y][x-1].visited:
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
            print("\033c")
            display_maze(maze)
            time.sleep(0.2)
        else:
            stack.pop()
    j, k = maze.entry
    ej, ek = maze.exit

    open_wall(maze, j, k)
    open_wall(maze, ej, ek)
    print("\033c")

def growing_tree(maze):
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
    → le ratio (0.7 ici) contrôle le style

    En gros :
    → meilleur rendu visuel que DFS pur
    """
    for row in maze.grid:
        for cell in row:
            cell.visited = False
            cell.generate = False

    cells = [(0, 0)]
    maze.grid[0][0].visited = True
    maze.grid[0][0].generate = True

    while cells:

        # choix du style (mix DFS / random)
        if random.random() < 0.7:
            index = -1  # DFS-like
        else:
            index = random.randint(0, len(cells) - 1)

        x, y = cells[index]

        neighbors = []

        if y > 0 and not maze.grid[y-1][x].visited:
            neighbors.append(("N", x, y-1))
        if x < maze.width - 1 and not maze.grid[y][x+1].visited:
            neighbors.append(("E", x+1, y))
        if y < maze.height - 1 and not maze.grid[y+1][x].visited:
            neighbors.append(("S", x, y+1))
        if x > 0 and not maze.grid[y][x-1].visited:
            neighbors.append(("W", x-1, y))

        if not neighbors:
            cells.pop(index)
            continue

        direction, nx, ny = random.choice(neighbors)

        current = maze.grid[y][x]
        next_cell = maze.grid[ny][nx]

        cells_braker(current, next_cell, direction)

        current.generate = True
        next_cell.generate = True

        print("\033c")
        display_maze(maze)
        time.sleep(0.05)

        next_cell.visited = True
        cells.append((nx, ny))

    open_wall(maze, *maze.entry)
    open_wall(maze, *maze.exit)
    print("\033c")


if __name__ == "__main__":
    r = open("config.txt", "r")
    config = parser_conf(r.read())
    height = int(config["HEIGHT"])
    width = int(config["WIDTH"])
    entry = tuple(map(int, config["ENTRY"].split(",")))
    exit_ = tuple(map(int, config["EXIT"].split(",")))
    maze_test = Maze(height, width, entry, exit_)
    # display_maze(maze_test)
    dfs(maze_test)
    add_loops(maze_test, 0.60)
    bfs(maze_test)
    # display_maze(maze_test)
