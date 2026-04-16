from typing import Any, Tuple
import time
from .generator import Maze, Cell
from .utils import RESET
from mlx import Mlx


class MlxError(Exception):
    pass


class InitError(MlxError):
    pass


class WindowError(MlxError):
    pass


class ImageError(MlxError):
    pass


class Window:
    """
    Initialize a window of 1000 pixels by 1000 pixels
    """
    def __init__(self) -> None:
        self.window: Any = None
        self.height: int = 1000
        self.width: int = 1000


class MazeCoord:
    """
    Store coordinates and dimensions of maze blocks.

    This class maintains the starting and ending
    X/Y coordinates for maze blocks. Positional
    values are calculated dynamically using the block
    size.
    """
    def __init__(self) -> None:
        self.x: int = 0
        self.x_s: int = 0
        self.x_e: int = 0
        self.y: int = 0
        self.y_s: int = 0
        self.y_e: int = 0


class Image:
    """
    Handle maze graphic rendering using the MiniLibX framework.

    This class manages the creation, pixel manipulation, and drawing of
    the maze onto an image buffer. It maps maze cells and paths to
    screen pixels based on a specified block size.

    Args:
        case (int): Size of a single maze cell in pixels.
        address (Any): Pointer to the raw image memory buffer.
        maze (Maze): The maze data structure to be rendered.
    """
    def __init__(self, case: int, maze: Maze) -> None:
        """Initialize the image renderer with cell size and maze data."""
        self.image: Any = None
        self.address: Any = None
        self.case: int = case
        self.red: int = 0xFFFF0000
        self.green: int = 0xFF00FF00
        self.purple: int = 0x88A9A9FF
        self.white: int = 0xFFFFFFFF
        self.black: int = 0xFF000000
        self.bpp: int = 0
        self.offset: int = 0
        self.maze: Maze = maze
        self.line_length: int = 0
        self.endian: int = 0
        self.p: MazeCoord = MazeCoord()

    def new_image(self, mlx: 'Render') -> None:
        """Create a new image buffer and retrieve its memory address."""
        img_w: int = self.maze.width * self.case
        img_h: int = self.maze.height * self.case
        self.image = mlx.mlx.mlx_new_image(mlx.init, img_w, img_h)
        if self.image is None:
            raise ImageError("[MLX_ERROR]: Error during creating image\n")
        addr, bpp, ll, end = mlx.mlx.mlx_get_data_addr(self.image)
        self.address = addr
        if self.address is None:
            raise ImageError("[MLX_ERROR]: Error during address assignation\n")
        self.bpp = bpp
        self.line_length = ll
        self.endian = end
        self.address = self.address.cast('I')
        self.offset = self.line_length // (self.bpp // 8)

    def put_pixel(self, x: int, y: int, color: int) -> None:
        """Draw a single pixel at (x, y) with the specified color."""
        self.address[y * self.offset + x] = color

    def put_case(self, col: int, row: int, color: int) -> None:
        """Fill a full maze cell at (col, row) with a specific color."""
        for y in range(self.case):
            for x in range(self.case):
                self.put_pixel(col * self.case + x, row * self.case + y, color)

    def wall(
        self,
        cell: Cell,
        x_s: int,
        y_s: int,
        x_e: int,
        y_e: int,
        color: int,
    ) -> None:
        """Draw cell walls based on North, South, West, East properties."""
        if cell.N:
            for i in range(self.case):
                self.put_pixel(x_s + i, y_s, color)
        if cell.S:
            for i in range(self.case):
                self.put_pixel(x_s + i, y_e, color)
        if cell.W:
            for i in range(self.case):
                self.put_pixel(x_s, y_s + i, color)
        if cell.E:
            for i in range(self.case):
                self.put_pixel(x_e, y_s + i, color)

    def draw_path(self, path: list[Tuple[int, int]], color: int) -> None:
        """Render the maze path using the specified color."""
        for cell in path:
            self.put_case(cell[0], cell[1], color)

    def draw_wall(
        self,
        cell: Cell,
        col: int,
        row: int,
        p: MazeCoord,
        color: int,
    ) -> None:
        """Determine wall placement for a cell and draw it."""
        if row == 0:
            self.wall(cell, p.x_s, p.y_s + 1, p.x_e, p.y_e, color)
        if row == self.maze.height - 1:
            self.wall(cell, p.x_s, p.y_s, p.x_e, p.y_e - 1, color)
        if col == 0:
            self.wall(cell, p.x_s + 1, p.y_s, p.x_e, p.y_e, color)
        if col == self.maze.width - 1:
            self.wall(cell, p.x_s - 1, p.y_s, p.x_e - 1, p.y_e, color)
        self.wall(cell, p.x_s, p.y_s, p.x_e, p.y_e, color)

    def draw_maze(self, path: bool) -> None:
        """Clear the buffer and render the full maze,
         including path and walls."""
        self.p = MazeCoord()
        for i in range(len(self.address)):
            self.address[i] = 0
        if path:
            self.draw_path(self.maze.path, self.purple)
        else:
            self.draw_path(self.maze.path, self.black)
        self.put_case(self.maze.entry[0], self.maze.entry[1], self.green)
        self.put_case(self.maze.exit[0], self.maze.exit[1], self.red)
        for row in range(self.maze.height):
            for col in range(self.maze.width):
                cell = self.maze.grid[row][col]
                self.p.x_s = col * self.case
                self.p.y_s = row * self.case
                self.p.x_e = ((col + 1) * self.case) - 1
                self.p.y_e = ((row + 1) * self.case) - 1
                self.draw_wall(cell, col, row, self.p, self.white)
                if cell.isftwo:
                    self.put_case(col, row, self.white)


class Render:
    """
    Handle the MiniLibX window and graphical rendering pipeline.

    This class manages the initialization of the MLX instance, the creation
    of the application window, and the refresh logic to switch between
    different visual states of the maze.

    Args:
        mlx (Mlx): Instance of the MiniLibX wrapper.
        init (Any): MLX initialization pointer.
        maze (Maze): Data structure of the maze being rendered.
        path_show (bool): State flag to toggle path visibility.
        w (Window): Window configuration object.
        case (int): Calculated pixel size for each maze cell.
    """
    def __init__(self, maze: Maze) -> None:
        """Initialize MLX engine and compute cell dimensions."""
        self.mlx: Mlx = Mlx()
        self.init: Any = self.mlx.mlx_init()
        if self.init is None:
            raise InitError("[MLX_ERROR]: Error initializing th instance\n")
        self.maze: Maze = maze
        self.path_show: bool = False
        self.w: Window = Window()
        self.case: int = int(
            min(self.w.height / self.maze.height,
                self.w.width / self.maze.width)
        )

    def new_window(self, name: str) -> None:
        """Create a new MLX window instance."""
        self.w.window = self.mlx.mlx_new_window(
            self.init, self.w.width, self.w.height, name)
        if self.w.window is None:
            raise WindowError("[MLX_ERROR]: Error during creating window\n")

    def refresh(self, image: Image, path: Image) -> None:
        """Update display based on path_show state."""
        if self.path_show:
            self.mlx.mlx_put_image_to_window(
                self.init, self.w.window, path.image, 0, 0)
        else:
            self.mlx.mlx_put_image_to_window(
                self.init, self.w.window, image.image, 0, 0)

    def close_window(self, param: Any) -> None:
        """Cleanup resources and exit MLX loop."""
        self.mlx.mlx_destroy_image(self.init, param[0].image)
        self.mlx.mlx_destroy_image(self.init, param[1].image)
        self.mlx.mlx_destroy_window(self.init, self.w.window)
        self.mlx.mlx_loop_exit(self.init)


def intro_animation(color: str) -> None:
    """
    Display an animated ASCII banner for the program.

    Prints a growing "A-MAZE-ING !!" text with character-by-character
    animation and surrounding border formatting.
    """
    text = "A-MAZE-ING"
    display = ""

    for char in text:
        display += char
        print("\033c", end="")
        print(color + "┌" + "───" * len(display) + "┐" + RESET)
        print(color + "│" + RESET, end="")
        for c in display:
            if c == "-":
                print(color + " _ " + RESET, end="")
            else:
                print(f" {c} ", end="")
        print(color + "│" + RESET)
        print(color + "└" + "───" * len(display) + "┘" + RESET)
        time.sleep(0.2)


def display_maze(
    maze: Maze,
    color: str,
    path: bool,
    forty_color: str = "\033[30m",
) -> None:
    """
    Render the maze in the terminal using ASCII characters.

    Args:
        maze: The Maze instance containing the grid and metadata.
        color: ANSI color code for maze structure.
        path: Toggle visibility of the solution path.
        forty_color: ANSI color code for the specific '42' logo styling.
    """
    COLOR_MAZE = color
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
            elif not cell.isbreakable:
                line1 += f"{forty_color}███{RESET}"
            elif (x, y) in maze.path and path:
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

        line2 = line2[:-1] + "│"
        print(line1)
        if y < height - 1:
            print(line2)

    print(COLOR_MAZE + "└" + "───┴" * (width - 1) + "───┘" + RESET)


def goodreturn(maze: Maze) -> Any:
    """
    Initialize the graphical rendering loop and manage window events.

    Sets up the Render environment, creates images for the base maze and
    path, and binds event hooks for key interaction. Returns the final
    state of the execution.

    Args:
        maze: The Maze instance to be rendered.
    """
    state: int = 0
    try:
        render: Render = Render(maze)
        render.new_window("A-Maze-Ing")
        image = Image(render.case, maze)
        path = Image(render.case, maze)
        image.new_image(render)
        path.new_image(render)
        image.draw_maze(False)
        path.draw_maze(True)
    except (Exception, ImageError, WindowError, InitError) as error:
        return 3, error

    def catch_key(key: int, params: Any) -> None:
        nonlocal state
        if key == 112:
            render.path_show = not render.path_show
            render.refresh(image, path)
        if key == 65307:
            state = 1
            render.close_window(params)
        elif key == 32:
            state = 2
            render.close_window(params)

    try:
        params = (image, path)
        render.mlx.mlx_put_image_to_window(render.init,
                                           render.w.window, image.image, 0, 0)
        render.mlx.mlx_key_hook(render.w.window, catch_key, params)
        render.mlx.mlx_hook(render.w.window, 33, 0, render.close_window, params)
        render.mlx.mlx_loop(render.init)
    except Exception as err:
        return 3, err
    return state, None
