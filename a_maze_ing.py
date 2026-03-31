import random

class Maze:
    def __init__(self, height, width, entry, exit_):
        self.height = height
        self.width = width
        self.entry = entry
        self.exit = exit_
        self.grid = []

        for y in range(height):
            row = []
            for x in range(width):
                row.append(Cell())
            self.grid.append(row)



class Cell:
    def __init__(self):
        self.N = True
        self.E = True
        self.S = True
        self.W = True
        self.visited = False


def open_wall(maze, x, y):
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
    height = maze.height
    width = maze.width

    print("┌" + "───┬" * (width - 1) + "───┐")

    for y in range(height):
        line1 = "│"
        line2 = "├"

        for x in range(width):
            cell = maze.grid[y][x]
            if (x, y) == maze.entry:
                line1 += " \033[33mo\033[0m "
            elif (x, y) == maze.exit:
                line1 += "\033[35m o \033[0m"
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

def dfs(maze):
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
            cells_braker(current, next_cell, direction)
            next_cell.visited = True
            stack.append((nx, ny))
        else:
            stack.pop()
    j, k = maze.entry
    ej, ek = maze.exit
    
    open_wall(maze, j, k)
    open_wall(maze, ej, ek)



if __name__ == "__main__":
    r = open("config.txt", "r")
    config = parser_conf(r.read())
    height = int(config["HEIGHT"])
    width = int(config["WIDTH"])
    entry = tuple(map(int, config["ENTRY"].split(".")))
    exit_ = tuple(map(int, config["EXIT"].split(".")))
    maze_test = Maze(height, width, entry, exit_)
    print("AVANT\n")
    display_maze(maze_test)
    dfs(maze_test)
    print("APRES\n")
    display_maze(maze_test)