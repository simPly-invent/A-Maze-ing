*This project has been created as part of the 42 curriculum by mobenais, celamarc.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator. The program reads a configuration file, generates a maze (perfect or not), displays it visually, and writes the result to an output file using a hexadecimal wall representation. The maze always contains a visible "42" pattern, and a BFS solver automatically computes the shortest path between the entry and the exit.

## Instructions

### Installation

```bash
make install
```

### Compilation / Run

```bash
# Install and run in one command
make

# Run the program
make run

# Debug mode
make debug

# Linter
make lint

# Clean
make clean

# Build the package
make build
```

### Usage

```bash
python3 a_maze_ing.py
```

The program automatically reads the `config.txt` file at the root of the project.

### Interactive Menu

Once launched, an interactive menu lets you:

1. Launch maze generation
2. Switch render mode (ASCII / MLX)
3. Switch algorithm (DFS / Growing Tree)
4. Toggle perfect / not perfect
5. Change maze dimensions
6. Change wall color
7. Show / hide the solution path
8. Exit the program

### Error Handling

```bash
# Config file not found
# -> Error: config.txt not found.

# Invalid values in config
# -> Displays the field name and the error message

# Entry or exit outside the maze
# -> Error: entry or exit outside of the maze
```

---

## Configuration File Format

The configuration file uses `KEY=VALUE` pairs (one per line). Lines starting with `#` are comments and are ignored.

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width (number of cells) | `WIDTH=20` |
| `HEIGHT` | Maze height (number of cells) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect maze (single path) | `PERFECT=True` |

Example `config.txt`:

```
# Maze configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

---

## Algorithm

### Chosen Algorithms

- **Generation**: DFS (Depth-First Search) and Growing Tree
- **Solving**: BFS (Breadth-First Search)

### How It Works

**DFS** explores the maze recursively by marking cells as visited. At each step, it picks an unvisited neighboring cell, removes the wall between them, and continues. When no unvisited neighbor is available, it backtracks.

**Growing Tree** works similarly but introduces randomness: at each step, it either picks the last added cell (DFS behavior) or a random cell from the active list. This random factor varies the texture and feel of the generated mazes.

**BFS** is used to solve the maze: it explores all reachable cells level by level from the entry, guaranteeing that the first path found to the exit is the shortest one.

When `PERFECT=False`, a `random_breaker` randomly removes ~10% of additional walls to create alternative paths.

### Why This Algorithm

DFS and Growing Tree were chosen for their simplicity and readability. They are a solid practical introduction to graphs and path-finding, which matched the learning goals of this project. BFS was selected for solving because it reliably guarantees the shortest path in a simple and efficient way.

---

## Code Reusability

### What Is Reusable

The `MazeGenerator` module (distributed as a `mazegen-*.whl` / `mazegen-*.tar.gz` package) is fully standalone and can be imported into any other Python project.

### How to Use It

```python
# Installation
pip install mazegen-1.0.0-py3-none-any.whl

# Basic usage
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=42, perfect=True)
maze = generator.generate()

# Access the maze structure
print(maze.grid)       # Cell grid
print(maze.solution)   # Solution path (list of directions: N/E/S/W)
```

### Custom Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | `int` | Maze width in cells |
| `height` | `int` | Maze height in cells |
| `seed` | `int` | Seed for reproducibility |
| `perfect` | `bool` | If `True`, only one path exists between entry and exit |

### Build the Package

```bash
# Inside a virtualenv
pip install poetry
poetry build
# Generates dist/mazegen-x.x.x.whl and dist/mazegen-x.x.x.tar.gz
```

---

## Team & Project Management

### Team Members

| Login | Contributions |
|-------|---------------|
| `mobenais` | DFS algorithm, Growing Tree, BFS solver, ASCII display, mazegen module, Makefile, interactive menu|
| `celamarc` | MLX display, Config file parsing, interactive menu, error handling, Makefile |

### Planning

The project started with setting up the config parser and the maze data structure. The generation algorithms were then developed in parallel with the display logic. The mazegen package and MLX render mode were finalized last. The overall timeline stayed close to the initial plan, with the main adjustment being extra time spent on the "42" pattern integration and wall coherence validation.

### What Worked Well

- The clear separation between generation, display, and solving made the code modular and easy to iterate on.
- The interactive menu allowed quick testing of different configurations without restarting the program.
- Using Pydantic for config validation caught errors early and kept the parsing clean.

### What Could Be Improved

- Setting up unit tests earlier in the development process would have caught edge cases sooner.
- The MLX render mode required more integration time than expected — planning for it earlier would have helped.

### Tools Used

- VSCode
- Discord (team communication)
- Poetry (packaging)
- mypy / flake8 (code quality)
- pytest (testing)

---

## Resources

### Documentation & References

- [Wikipedia - Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Wikipedia - Depth-First Search](https://en.wikipedia.org/wiki/Depth-first_search)
- [Wikipedia - Breadth-First Search](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python `typing` module](https://docs.python.org/3/library/typing.html)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Poetry documentation](https://python-poetry.org/docs/)

### AI Usage

AI was used to help write and structure the README. All code was written and fully understood by the project authors.
