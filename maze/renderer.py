from typing import Any, Tuple
import time
from .generator import Maze, Cell
from .utils import RESET
from mlx import Mlx


class Window:
    def __init__(self) -> None:
        self.window: Any = None
        self.height: int = 1000
        self.width: int = 1000


class MazeCoord:
    def __init__(self) -> None:
        self.x: int = 0
        self.x_s: int = 0
        self.x_e: int = 0
        self.y: int = 0
        self.y_s: int = 0
        self.y_e: int = 0


class Image:
    def __init__(self, case: int, maze: Maze) -> None:
        self.image: Any = None
        self.address: Any = None
        self.case: int = case
        self.red: int = 0xFFFF0000
        self.green: int = 0xFF00FF00
        self.purple: int = 0xA9A9A9FF
        self.white: int = 0xFFFFFFFF
        self.black: int = 0xFF000000
        self.bpp: int = 0
        self.offset: int = 0
        self.maze: Maze = maze
        self.line_length: int = 0
        self.endian: int = 0
        self.p: MazeCoord = MazeCoord()

    def new_image(self, mlx: 'Render') -> None:
        img_w: int = self.maze.width * self.case
        img_h: int = self.maze.height * self.case
        self.image = mlx.mlx.mlx_new_image(mlx.init, img_w, img_h)
        addr, bpp, ll, end = mlx.mlx.mlx_get_data_addr(self.image)
        self.address = addr
        self.bpp = bpp
        self.line_length = ll
        self.endian = end
        self.address = self.address.cast('I')
        self.offset = self.line_length // (self.bpp // 8)

    def put_pixel(self, x: int, y: int, color: int) -> None:
        self.address[y * self.offset + x] = color

    def put_case(self, col: int, row: int, color: int) -> None:
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
        self.p = MazeCoord()
        for i in range(1000 * 1000):
            self.address[i] = 0
        if path:
            print("path drown")
            self.draw_path(self.maze.path, self.purple)
        else:
            print("path not drown")
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
    def __init__(self, maze: Maze) -> None:
        self.mlx: Mlx = Mlx()
        self.init: Any = self.mlx.mlx_init()
        self.maze: Maze = maze
        self.path_show: bool = False
        self.w: Window = Window()
        self.case: int = int(
            min(self.w.height / self.maze.height, self.w.width / self.maze.width)
        )

    def new_window(self, name: str) -> None:
        self.w.window: Any = self.mlx.mlx_new_window(
            self.init, self.w.width, self.w.height, name
        )

    def refresh(self, image: Image, path: Image) -> None:
        if self.path_show:
            self.mlx.mlx_put_image_to_window(
                self.init, self.w.window, path.image, 0, 0
            )
        else:
            self.mlx.mlx_put_image_to_window(
                self.init, self.w.window, image.image, 0, 0
            )

    def close_window(self, param: Any) -> int:
        self.mlx.mlx_destroy_image(self.init, param.image)
        self.mlx.mlx_destroy_window(self.init, self.w.window)
        self.mlx.mlx_loop_exit(self.init)
        return 0


def intro_animation(color: str) -> None:
    text = "A-MAZE-ING !!"
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
    path: bool = True,
    forty_color: str = "\033[30m",
) -> None:
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


def test(key: int, params: Any) -> None:
    render, image, path = params


def goodreturn(maze: Maze) -> int:
    state: int = 0
    render: Render = Render(maze)
    render.new_window("A-Maze-Ing")
    image = Image(render.case, maze)
    path = Image(render.case, maze)
    image.new_image(render)
    path.new_image(render)
    image.draw_maze(False)
    path.draw_maze(True)

    def catch_key(key: int, params: Any) -> int:
        nonlocal state
        print(key)
        if key == 112:
            render.path_show = not render.path_show
            render.refresh(image, path)
            return 0
        if key == 65307:
            state = 1
            render.close_window(image)
        elif key == 32:
            state = 2
            render.close_window(image)
        return 0

    params = (image, path)
    render.mlx.mlx_put_image_to_window(render.init, render.w.window, image.image, 0, 0)
    render.mlx.mlx_key_hook(render.w.window, catch_key, params)
    render.mlx.mlx_hook(render.w.window, 33, 0, render.close_window, image)
    render.mlx.mlx_loop(render.init)
    return state