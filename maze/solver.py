from . import generator


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
    maze.grid[0][0].isbreakable = False
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
            break
        neighbors = []

        if y > 0 and not maze.grid[y-1][x].visited and maze.grid[y-1][x].isbreakable:
            neighbors.append(("N", x, y-1))

        if x < maze.width - 1 and not maze.grid[y][x+1].visited and maze.grid[y][x+1].isbreakable:
            neighbors.append(("E", x+1, y))

        if y < maze.height - 1 and not maze.grid[y+1][x].visited and maze.grid[y+1][x].isbreakable:
            neighbors.append(("S", x, y+1))

        if x > 0 and not maze.grid[y][x-1].visited and maze.grid[y][x-1].isbreakable:
            neighbors.append(("W", x-1, y))

        for neighbor in neighbors:
            direction, nx, ny = neighbor
            coordinate = x, y
            good_way = no_wall(direction, maze, coordinate)
            if good_way and not maze.grid[ny][nx].visited and maze.grid[ny][nx].isbreakable:
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