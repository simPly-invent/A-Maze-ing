from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maze import Maze


def no_wall(direction: str, maze: "Maze", coordinate: tuple[int, int]) -> bool:
    """
    Check whether a passage exists in the given direction from a cell.

    Args:
        direction: One of "N", "E", "S", "W".
        maze: The Maze object containing the grid.
        coordinate: (x, y) position of the cell to inspect.

    Returns:
        True if the wall in that direction is open, False otherwise.
    """
    x, y = coordinate
    cell = maze.grid[y][x]
    return {
        "N": not cell.N,
        "E": not cell.E,
        "S": not cell.S,
        "W": not cell.W,
    }.get(direction, False)


def bfs(maze: "Maze") -> None:
    """
    Find the shortest path between the entry and the exit using BFS.

    The algorithm runs a FIFO breadth-first search from the maze entry:
        1. Start from the entry cell and mark it visited.
        2. Explore all reachable neighbours (no wall, not visited, breakable).
        3. Record each cell's parent to allow path reconstruction.
        4. Stop as soon as the exit cell is dequeued.
        5. Walk back through the parent map to build the final path.

    Result:
        ``maze.path`` is populated with the ordered list of (x, y) coordinates
        from entry to exit (inclusive). If no path exists, the list is empty.

    Note:
        BFS guarantees the shortest path and handles mazes with loops correctly.

    Args:
        maze: The Maze object to solve. Its ``path`` attribute is overwritten.
    """
    maze.path = []

    for row in maze.grid:
        for cell in row:
            cell.visited = False

    x, y = maze.entry
    queue: deque[tuple[int, int]] = deque([(x, y)])
    maze.grid[y][x].visited = True
    parent: dict[tuple[int, int], tuple[int, int]] = {}

    while queue:
        x, y = queue.popleft()

        if (x, y) == maze.exit:
            break

        n = maze.grid[y - 1][x] if y > 0 else None
        e = maze.grid[y][x + 1] if x < maze.width - 1 else None
        s = maze.grid[y + 1][x] if y < maze.height - 1 else None
        w = maze.grid[y][x - 1] if x > 0 else None

        candidates: list[tuple[str, int, int]] = []
        if n:
            candidates.append(("N", x, y - 1))
        if e:
            candidates.append(("E", x + 1, y))
        if s:
            candidates.append(("S", x, y + 1))
        if w:
            candidates.append(("W", x - 1, y))

        for direction, nx, ny in candidates:
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