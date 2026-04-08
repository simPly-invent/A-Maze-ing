import random
import time

from mlx import Mlx
from pydantic import BaseModel, Field, model_validator

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


class Config(BaseModel):
    WIDTH: int = Field(ge=0, le=1000)
    HEIGHT: int = Field(ge=0, le=1000)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    PERFECT: bool

    @model_validator(mode="after")
    def check_rules(self):
        if self.WIDTH == 3 and self.HEIGHT == 3:
            raise ValueError("maze to small to be create")
        return self


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
    COLOR_MAZE = RED
    height = maze.height
    width = maze.width

    print(COLOR_MAZE + "┌" + "───┬" * (width - 1) + "───┐" + RESET)

    for y in range(height):
        line1 = f"{COLOR_MAZE}│{RESET}"
        line2 = f"{COLOR_MAZE}├{RESET}"

        for x in range(width):
            cell = maze.grid[y][x]
            if not cell.generate:
                line1 += "   "
                line1 += f"{COLOR_MAZE}│{RESET}"
                continue
            if (x, y) == maze.entry:
                line1 += " \033[33mo\033[0m "
            elif (x, y) == maze.exit:
                line1 += "\033[35m o \033[0m"
            elif (x, y) in maze.path:
                line1 += " x "
            else:
                line1 += "   "

            if cell.E:
                line1 += f"{COLOR_MAZE}│{RESET}"
            else:
                line1 += " "

            if cell.S:
                line2 += f"{COLOR_MAZE}───┼{RESET}"
            else:
                line2 += f"   {COLOR_MAZE}┼{RESET}"

        # line1 = line1[:-1] + f"{COLOR_MAZE}│{RESET}"
        line2 = line2[:-1] + f"│"

        print(line1)

        if y < height - 1:
            print(line2)

    print(COLOR_MAZE + "└" + "───┴" * (width - 1) + "───┘" + RESET)


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

        if y > 0 and not maze.grid[y - 1][x].visited:
            neighbors.append(("N", x, y - 1))

        if x < maze.width - 1 and not maze.grid[y][x + 1].visited:
            neighbors.append(("E", x + 1, y))

        if y < maze.height - 1 and not maze.grid[y + 1][x].visited:
            neighbors.append(("S", x, y + 1))

        if x > 0 and not maze.grid[y][x - 1].visited:
            neighbors.append(("W", x - 1, y))

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
    # display_maze(maze)


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
            time.sleep(0.001)
        else:
            stack.pop()
    j, k = maze.entry
    ej, ek = maze.exit

    open_wall(maze, j, k)
    open_wall(maze, ej, ek)
    print("\033c")


def window(maze, maze_HEIGHT, maze_WIDTH):
    def win_close(key, *param):
        if key == 65307:
            mlx.mlx_loop_exit(param[0])

    def put_pixel(img_adr, offset, x, y, color):
        img_adr[y * offset + x] = color


    def put_case(maze, width, height, img_adr, offset, color, tile):
        blue = 0xFF0000FF
        green = 0xFF00FF00
        white = 0xFFFFFFFF
        wall = 2
        for col in range(height):
            for row in range(width):
                cell = maze.grid[row][col]
                for y in range(tile):
                    for x in range(tile):
                        if (col, row) == maze.entry:
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), blue)
                        elif (col, row) == maze.exit:
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), green)
                        elif (col, row) in maze.path:
                            color = 0xA9A9A9FF
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), color)
                        if (cell.N and y < wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)
                        elif (cell.S and y >= tile - wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)
                        if (cell.E and x >= tile - wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)
                        elif (cell.W and x < wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)


    mlx = Mlx()

    tile_size = 50

    init = mlx.mlx_init()

    mlx_win = mlx.mlx_new_window(init, maze_WIDTH * tile_size, maze_HEIGHT * tile_size, "a-maze-ing")
    mlx_img = mlx.mlx_new_image(init, maze_WIDTH * tile_size, maze_HEIGHT * tile_size)
    img_adr, bpp, line_length, endian = mlx.mlx_get_data_addr(mlx_img)
    img_adr = img_adr.cast('I')
    offset = line_length // (bpp // 8)

    put_case(maze, maze_WIDTH, maze_HEIGHT, img_adr, offset, 0, tile_size)
    mlx.mlx_put_image_to_window(init, mlx_win, mlx_img, 0, 0)
    mlx.mlx_key_hook(mlx_win, win_close, init)
    mlx.mlx_loop(init)


if __name__ == "__main__":
    r = open("config.txt", "r")
    config = parser_conf(r.read())
    maze_conf = Config(
        WIDTH=int(config["WIDTH"]),
        HEIGHT=int(config["HEIGHT"]),
        ENTRY=tuple(map(int, config["ENTRY"].split(","))),
        EXIT=tuple(map(int, config["EXIT"].split(","))),
        PERFECT=config["PERFECT"].lower() == "true")
    perfect = maze_conf.PERFECT
    maze_test = Maze(maze_conf.HEIGHT, maze_conf.WIDTH, maze_conf.ENTRY, maze_conf.EXIT)
    dfs(maze_test)
    if not perfect:
        add_loops(maze_test, 0.40)
    bfs(maze_test)
    display_maze(maze_test)
    window(maze_test, maze_conf.HEIGHT, maze_conf.WIDTH)
