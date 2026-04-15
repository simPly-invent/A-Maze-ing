import random
import time
from typing import Optional, Tuple
from .solver import bfs


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
        seed: Optional[int],
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit_: Tuple[int, int] = exit_
        self.seed: Optional[int] = seed
        if self.seed is not None:
            random.seed(self.seed)
        self.maze: Optional[Maze] = None
        self.solution: Optional[list[Tuple[int, int]]] = None
        self.start_gen: Tuple[int, int] = (0, 0)

    def generate(
        self,
        algo: str = "dfs",
        start: Tuple[int, int] = (0, 0),
    ) -> None:
        self.start_gen = start
        self.maze = Maze(self.width, self.height, self.entry, self.exit_)
        if algo == "dfs":
            dfs(self.maze)
        elif algo == "growing_tree":
            growing_tree(self.maze, self.start_gen[0], self.start_gen[1])
        bfs(self.maze)
        self.solution = self.maze.path


class Cell:
    """
    Represents a single cell in the maze.

    Attributes:
        N, E, S, W: Walls on each side.
        isbreakable: Whether the wall can be broken during generation.
        visited: Used during DFS / BFS traversal.
        generate: Used during display while generating.
        isftwo: Whether the cell belongs to the 42 pattern.

    In short:
        Each cell knows where its walls are and whether it has been visited.
    """

    def __init__(self) -> None:
        self.N: bool = True
        self.E: bool = True
        self.S: bool = True
        self.W: bool = True
        self.isbreakable: bool = True
        self.visited: bool = False
        self.generate: bool = False
        self.isftwo: bool = False


class Maze:
    """
    Represents the full maze structure.

    Attributes:
        height: Number of rows.
        width: Number of columns.
        entry: Entry point coordinates (x, y).
        exit: Exit point coordinates (x, y).
        grid: 2D list of Cell objects.
        path: Path found by BFS (list of (x, y) coordinates).

    In short:
        The main data structure that holds the entire maze state.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_: Tuple[int, int],
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit_
        self.grid: list[list[Cell]] = []
        self.path: list[Tuple[int, int]] = []

        for y in range(height):
            row: list[Cell] = []
            for x in range(width):
                row.append(Cell())
            self.grid.append(row)


def open_wall(maze: Maze, x: int, y: int) -> None:
    """
    Open a wall on the border of the maze.

    Used to create the entry and exit openings.

    The function checks which border the cell is on and removes
    the corresponding wall:
        - y == 0          -> open North wall
        - y == height - 1 -> open South wall
        - x == 0          -> open West wall
        - x == width - 1  -> open East wall
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


def cells_breaker(current: Cell, next_cell: Cell, direction: str) -> None:
    """
    Break the wall between two adjacent cells.

    Args:
        current: The current cell.
        next_cell: The neighbouring cell to connect to.
        direction: One of "N", "E", "S", "W".

    Both sides of the wall are removed so the passage is bidirectional.
    If either cell is not breakable, the function returns without change.

    Example:
        direction == "E" -> current.E = False AND next_cell.W = False
    """
    if not current.isbreakable or not next_cell.isbreakable:
        return
    if direction == "E":
        current.E = False
        next_cell.W = False
    elif direction == "S":
        current.S = False
        next_cell.N = False
    elif direction == "W":
        current.W = False
        next_cell.E = False
    elif direction == "N":
        current.N = False
        next_cell.S = False


def convert_bit(cell: Cell) -> int:
    """
    Encode a cell's wall state as a 4-bit integer.

    Bit layout (LSB first): N=bit0, E=bit1, S=bit2, W=bit3.

    Returns:
        An integer in [0, 15] representing the wall configuration.
    """
    return (
        int(cell.N) << 0
        | int(cell.E) << 1
        | int(cell.S) << 2
        | int(cell.W) << 3
    )


def convert_maze_output(maze: Maze, output: str) -> None:
    """
    Write the maze state to 'outputfile.txt'.

    Output format:
        - One hex-encoded row per line (wall bitmask per cell).
        - Blank line separator.
        - Entry coordinates: "x,y".
        - Exit coordinates: "x,y".
        - Direction sequence of the solution path (e.g. "SSEEN...").
    """
    direction: Optional[str]
    with open(output, "w") as f:
        for y in range(maze.height):
            for x in range(maze.width):
                f.write(f"{format(convert_bit(maze.grid[y][x]), 'X')}")
            f.write("\n")
        f.write("\n")
        f.write(f"{maze.entry[0]},{maze.entry[1]}\n")
        f.write(f"{maze.exit[0]},{maze.exit[1]}\n")
        for i in range(len(maze.path) - 1):
            current_pos = maze.path[i]
            next_pos = maze.path[i + 1]
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            direction = None
            if dy == +1:
                direction = "S"
            elif dy == -1:
                direction = "N"
            elif dx == +1:
                direction = "W"
            elif dx == -1:
                direction = "E"
            if direction is not None:
                f.write(direction)


def initforty_two(maze: Maze) -> None:
    """
    Carve the '42' pattern into the centre of the maze.

    Cells that belong to the pattern are marked as non-breakable so
    the generation algorithm cannot remove their walls.
    """
    pattern = [
        "4 4 222",
        "4 4   2",
        "444 222",
        "  4 2  ",
        "  4 222",
    ]
    start_x = maze.width // 2 - len(pattern[0]) // 2
    start_y = maze.height // 2 - len(pattern) // 2

    for dy, row in enumerate(pattern):
        for dx, char in enumerate(row):
            if char != " ":
                cell = maze.grid[start_y + dy][start_x + dx]
                cell.isbreakable = False
                cell.generate = True
                cell.isftwo = True


def dfs(
    maze: Maze,
    color: Optional[str] = None,
    type_display: Optional[str] = None,
) -> None:
    """
    Generate a maze using Depth-First Search (recursive backtracker).

    The algorithm works as follows:
        1. Push the starting cell onto a stack and mark it visited.
        2. Pick a random unvisited neighbour, break the shared wall,
           and push the neighbour onto the stack.
        3. If no unvisited neighbours exist, backtrack (pop the stack).
        4. Repeat until the stack is empty.

    The result is a *perfect* maze (exactly one path between any two cells).
    An optional ASCII animation can be displayed at each step.

    Args:
        maze: The Maze object to generate into.
        color: Color parameter forwarded to the renderer.
        type_display: Pass "ascii" to enable step-by-step animation.
    """
    from .renderer import display_maze

    stack: list[Tuple[int, int]] = [(0, 0)]
    maze.grid[0][0].visited = True

    while stack:
        x, y = stack[-1]
        neighbors: list[Tuple[str, int, int]] = []

        n = maze.grid[y - 1][x] if y > 0 else None
        e = maze.grid[y][x + 1] if x < maze.width - 1 else None
        s = maze.grid[y + 1][x] if y < maze.height - 1 else None
        w = maze.grid[y][x - 1] if x > 0 else None
        if n and not n.visited and n.isbreakable:
            neighbors.append(("N", x, y - 1))
        if e and not e.visited and e.isbreakable:
            neighbors.append(("E", x + 1, y))
        if s and not s.visited and s.isbreakable:
            neighbors.append(("S", x, y + 1))
        if w and not w.visited and w.isbreakable:
            neighbors.append(("W", x - 1, y))

        if neighbors:
            direction, nx, ny = random.choice(neighbors)
            current = maze.grid[y][x]
            next_cell = maze.grid[ny][nx]
            current.generate = True
            next_cell.generate = True
            cells_breaker(current, next_cell, direction)
            next_cell.visited = True
            stack.append((nx, ny))
            if type_display == "ascii":
                print("\033c")
                display_maze(maze, color)
                time.sleep(0.05)
        else:
            stack.pop()

    open_wall(maze, *maze.entry)
    open_wall(maze, *maze.exit)
    print("\033c")


def random_breaker(maze: Maze, chance: float = 0.1) -> None:
    """
    Randomly remove extra walls to create loops in the maze.

    Iterates over every cell and, with probability *chance*, breaks the
    East or South wall to an adjacent breakable cell. This turns a perfect
    maze into a maze with multiple paths (braided maze).

    Args:
        maze: The Maze object to modify.
        chance: Probability [0.0, 1.0] that any given wall is removed.
    """
    for y in range(maze.height):
        for x in range(maze.width):
            if x < maze.width - 1:
                if random.random() < chance:
                    c1, c2 = maze.grid[y][x], maze.grid[y][x + 1]
                    if c1.isbreakable and c2.isbreakable:
                        cells_breaker(c1, c2, "E")
                        c1.generate = c2.generate = True
            if y < maze.height - 1:
                if random.random() < chance:
                    c1, c2 = maze.grid[y][x], maze.grid[y + 1][x]
                    if c1.isbreakable and c2.isbreakable:
                        cells_breaker(c1, c2, "S")
                        c1.generate = c2.generate = True


def growing_tree(
    maze: Maze,
    x: int,
    y: int,
    color: Optional[str] = None,
    type_display: Optional[str] = None,
) -> None:
    """
    Generate a maze using the Growing Tree algorithm.

    This algorithm blends DFS and random selection:
        - Maintain an active list of cells.
        - With 50 % probability pick the last cell (DFS-like behaviour).
        - Otherwise pick a random cell from the list (more open layout).
        - Break the wall to a random unvisited neighbour and add it to the list.
        - Remove a cell from the list when it has no more unvisited neighbours.

    The result is less rigid than pure DFS and produces more natural-looking
    mazes. An optional ASCII animation can be displayed at each step.

    Args:
        maze: The Maze object to generate into.
        x: Starting column index.
        y: Starting row index.
        color: Color parameter forwarded to the renderer.
        type_display: Pass "ascii" to enable step-by-step animation.
    """
    from .renderer import display_maze

    for row in maze.grid:
        for cell in row:
            if cell.isbreakable:
                cell.visited = False
                cell.generate = False

    cells: list[Tuple[int, int]] = [(y, x)]
    maze.grid[y][x].visited = True
    maze.grid[y][x].generate = True

    while cells:
        idx = -1 if random.random() < 0.5 else random.randint(0, len(cells) - 1)
        cx, cy = cells[idx]

        neighbors: list[Tuple[str, int, int]] = []

        n = maze.grid[cy - 1][cx] if cy > 0 else None
        e = maze.grid[cy][cx + 1] if cx < maze.width - 1 else None
        s = maze.grid[cy + 1][cx] if cy < maze.height - 1 else None
        w = maze.grid[cy][cx - 1] if cx > 0 else None
        if n and not n.visited and n.isbreakable:
            neighbors.append(("N", cx, cy - 1))
        if e and not e.visited and e.isbreakable:
            neighbors.append(("E", cx + 1, cy))
        if s and not s.visited and s.isbreakable:
            neighbors.append(("S", cx, cy + 1))
        if w and not w.visited and w.isbreakable:
            neighbors.append(("W", cx - 1, cy))

        if not neighbors:
            cells.pop(idx)
            continue

        direction, nx, ny = random.choice(neighbors)
        current = maze.grid[cy][cx]
        next_cell = maze.grid[ny][nx]

        if current.isbreakable and next_cell.isbreakable:
            cells_breaker(current, next_cell, direction)
            current.generate = True
            next_cell.generate = True
            next_cell.visited = True
            cells.append((nx, ny))

        if type_display == "ascii":
            print("\033c")
            display_maze(maze, color, True)
            time.sleep(0.04)

    open_wall(maze, *maze.entry)
    open_wall(maze, *maze.exit)
    print("\033c")
