import random


class Cell:
    def __init__(self):
        self.N = True
        self.E = True
        self.S = True
        self.W = True
        self.visited = False


def display_maze(maze):
    height = len(maze)
    width = len(maze[0])
    
    print("+" + "---+" * width)
    for y in range(height):
        line1 = "|"
        line2 = "+"

        for x in range(width):
            cell = maze[y][x]
            line1 += "   "
            if cell.E:
                line1 += "|"
            else:
                line1 += " "
            if cell.S:
                line2 += "---+"
            else:
                line2 += "   +"
        print(line1)
        print(line2)

def parser_conf(data):
    config_dico = {}
    first_tab = data.split("\n")
    for element in first_tab:
        second_tab = element.split("=")
        KEY = second_tab[0]
        VALUE = second_tab[1]
        config_dico[KEY] = VALUE
    return(config_dico)

def cells_maker(width, height):
    maze = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(Cell())
        maze.append(row)
    return maze


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

def dfs(maze, width, height):
    stack = [(0, 0)]
    maze[0][0].visited = True

    while stack:
        x, y = stack[-1]

        # récupérer voisins non visités
        neighbors = []

        # haut
        if y > 0 and not maze[y-1][x].visited:
            neighbors.append(("N", x, y-1))

        # droite
        if x < width-1 and not maze[y][x+1].visited:
            neighbors.append(("E", x+1, y))

        # bas
        if y < height-1 and not maze[y+1][x].visited:
            neighbors.append(("S", x, y+1))

        # gauche
        if x > 0 and not maze[y][x-1].visited:
            neighbors.append(("W", x-1, y))

        if neighbors:
            direction, nx, ny = random.choice(neighbors)

            current = maze[y][x]
            next_cell = maze[ny][nx]

            # casser mur (tu dois compléter)
            cells_braker(current, next_cell, direction)

            next_cell.visited = True
            stack.append((nx, ny))
        else:
            stack.pop()





if __name__ == "__main__":
    r = open("config.txt", "r")
    config = parser_conf(r.read())
    height = config["HEIGHT"]
    width = config["WIDTH"]
    maze_test = cells_maker(int(width), int(height))
    dfs(maze_test, int(width), int(height))
    display_maze(maze_test)