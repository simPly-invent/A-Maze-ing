from collections import deque
import random
from typing import Optional


class MazeGenerator:
    def __init__(self, height: int, width: int, entry: tuple[int, int],
                 exit_: tuple[int, int], seed: Optional[int]) -> None:
        self.height = height
        self.width = width
        self.entry = entry
        self.exit_ = exit_
        self.seed = seed
        if self.seed is not None:
            random.seed(self.seed)
        self.maze: Optional[Maze] = None
        self.solution: Optional[list[tuple[int, int]]] = None

    def generate(self, algo: str = "dfs",
                 start: tuple[int, int] = (0, 0)) -> None:
        self.start_gen = start
        self.maze = Maze(self.height, self.width, self.entry, self.exit_)
        if algo == "dfs":
            dfs(self.maze)
        elif algo == "growing_tree":
            growing_tree(self.maze, self.start_gen[0], self.start_gen[1])
        bfs(self.maze)
        self.solution = self.maze.path


class Cell:
    """Represents a single cell in the maze."""

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
    """Represents the full maze structure."""

    def __init__(
        self,
        height: int,
        width: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> None:
        self.height = height
        self.width = width
        self.entry = entry
        self.exit = exit_
        self.grid: list[list[Cell]] = []
        self.path: list[tuple[int, int]] = []

        for _ in range(height):
            row: list[Cell] = []
            for _ in range(width):
                row.append(Cell())
            self.grid.append(row)


def open_wall(maze: Maze, x: int, y: int) -> None:
    """Open a wall on the border of the maze."""
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
    """Break the wall between two adjacent cells."""
    if not current.isbreakable or not next_cell.isbreakable:
        return
    if direction == "E":
        current.E, next_cell.W = False, False
    elif direction == "S":
        current.S, next_cell.N = False, False
    elif direction == "W":
        current.W, next_cell.E = False, False
    elif direction == "N":
        current.N, next_cell.S = False, False


def dfs(maze: Maze) -> None:
    """Generate a maze using Depth-First Search."""
    stack: list[tuple[int, int]] = [(0, 0)]
    maze.grid[0][0].visited = True

    while stack:
        x, y = stack[-1]
        neighbors: list[tuple[str, int, int]] = []

        possible = [
            ("N", x, y - 1), ("E", x + 1, y),
            ("S", x, y + 1), ("W", x - 1, y)
        ]

        for d, nx, ny in possible:
            if 0 <= nx < maze.width and 0 <= ny < maze.height:
                target = maze.grid[ny][nx]
                if not target.visited and target.isbreakable:
                    neighbors.append((d, nx, ny))

        if neighbors:
            direction, nx, ny = random.choice(neighbors)
            current, next_cell = maze.grid[y][x], maze.grid[ny][nx]
            current.generate = next_cell.generate = True
            cells_breaker(current, next_cell, direction)
            next_cell.visited = True
            stack.append((nx, ny))
        else:
            stack.pop()

    open_wall(maze, *maze.entry)
    open_wall(maze, *maze.exit)


def random_breaker(maze: Maze, chance: float = 0.1) -> None:
    """Randomly remove extra walls to create loops in the maze."""
    for y in range(maze.height):
        for x in range(maze.width):
            if x < maze.width - 1 and random.random() < chance:
                c1, c2 = maze.grid[y][x], maze.grid[y][x + 1]
                if c1.isbreakable and c2.isbreakable:
                    cells_breaker(c1, c2, "E")
                    c1.generate = c2.generate = True
            if y < maze.height - 1 and random.random() < chance:
                c1, c2 = maze.grid[y][x], maze.grid[y + 1][x]
                if c1.isbreakable and c2.isbreakable:
                    cells_breaker(c1, c2, "S")
                    c1.generate = c2.generate = True


def growing_tree(maze: Maze, x: int, y: int) -> None:
    """Generate a maze using the Growing Tree algorithm."""
    for row in maze.grid:
        for cell in row:
            if cell.isbreakable:
                cell.visited, cell.generate = False, False

    cells: list[tuple[int, int]] = [(x, y)]
    maze.grid[y][x].visited = True
    maze.grid[y][x].generate = True

    while cells:
        i = -1 if random.random() < 0.5 else random.randint(0, len(cells) - 1)
        cx, cy = cells[i]
        neighbors: list[tuple[str, int, int]] = []
        possible = [
            ("N", cx, cy - 1), ("E", cx + 1, cy),
            ("S", cx, cy + 1), ("W", cx - 1, cy)
        ]
        for d, nx, ny in possible:
            if 0 <= nx < maze.width and 0 <= ny < maze.height:
                target = maze.grid[ny][nx]
                if not target.visited and target.isbreakable:
                    neighbors.append((d, nx, ny))

        if not neighbors:
            cells.pop(i)
            continue

        direction, nx, ny = random.choice(neighbors)
        current, next_cell = maze.grid[cy][cx], maze.grid[ny][nx]

        if current.isbreakable and next_cell.isbreakable:
            cells_breaker(current, next_cell, direction)
            current.generate = next_cell.generate = True
            next_cell.visited = True
            cells.append((nx, ny))

    open_wall(maze, *maze.entry)
    open_wall(maze, *maze.exit)


def no_wall(direction: str, maze: Maze, coordinate: tuple[int, int]) -> bool:
    """Check whether a passage exists in the given direction."""
    x, y = coordinate
    cell = maze.grid[y][x]
    return {
        "N": not cell.N,
        "E": not cell.E,
        "S": not cell.S,
        "W": not cell.W,
    }.get(direction, False)


def bfs(maze: Maze) -> None:
    """Find the shortest path using BFS."""
    maze.path = []

    for row in maze.grid:
        for cell in row:
            cell.visited = False

    sx, sy = maze.entry
    queue: deque[tuple[int, int]] = deque([(sx, sy)])
    maze.grid[sy][sx].visited = True
    parent: dict[tuple[int, int], tuple[int, int]] = {}

    while queue:
        x, y = queue.popleft()

        if (x, y) == maze.exit:
            break

        possible = [
            ("N", x, y - 1), ("E", x + 1, y),
            ("S", x, y + 1), ("W", x - 1, y)
        ]

        for direction, nx, ny in possible:
            if 0 <= nx < maze.width and 0 <= ny < maze.height:
                neighbour = maze.grid[ny][nx]
                if (
                    no_wall(direction, maze, (x, y))
                    and not neighbour.visited
                    and neighbour.isbreakable
                ):
                    neighbour.visited = True
                    parent[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

    position = maze.exit
    while position in parent:
        maze.path.append(position)
        position = parent[position]
    maze.path.append(maze.entry)
    maze.path.reverse()
