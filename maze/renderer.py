from typing import Any, Optional, Union, cast
import time
from .generator import Maze, Cell  # Assumé selon ton code
from .utils import RESET           # Assumé selon ton code
from mlx import Mlx


class Window:
    def __init__(self, width: int, height: int) -> None:
        self.window: Any = None
        self.bpp: int = 0
        self.offset: int = 0
        if height < 0:
            self.height: int = 0
        else:
            self.height = height
        if width < 0:
            self.width: int = 0
        else:
            self.width = width


class Image:
    def __init__(self, case: int) -> None:
        self.image: Any = None
        self.address: Any = None
        if case < 0:
            self.case: int = 32
        else:
            self.case = case
        self.red: int = 0xFFFF0000
        self.green: int = 0xFF00FF00
        self.purple: int = 0xA9A9A9FF
        self.grey: int = 0xCCFFFFFF
        self.white: int = 0xFFFFFFFF


class MazeCoord:
    def __init__(self) -> None:
        self.x: int = 0
        self.x_start: int = 0
        self.x_end: int = 0
        self.y: int = 0
        self.y_start: int = 0
        self.y_end: int = 0


class Render:
    def __init__(self, width: int, height: int, case: int) -> None:
        self.mlx: Mlx = Mlx()
        self.init: Any = self.mlx.mlx_init()
        self.w: Window = Window(width, height)
        self.i: Image = Image(case)
        self.line_length: int = 0
        self.endian: int = 0
        self.pixel: MazeCoord = MazeCoord()

    def new_window(self, name: str) -> None:
        width_px = self.w.width * self.i.case
        height_px = self.w.height * self.i.case + 150
        self.w.window = self.mlx.mlx_new_window(self.init, width_px, height_px, name)

    def new_image(self) -> None:
        img_w = self.w.width * self.i.case
        img_h = self.w.height * self.i.case
        self.i.image = self.mlx.mlx_new_image(self.init, img_w, img_h)
        addr, bpp, ll, end = self.mlx.mlx_get_data_addr(self.i.image)
        self.i.address = addr
        self.w.bpp = bpp
        self.line_length = ll
        self.endian = end
        self.i.address = self.i.address.cast('I')
        self.w.offset = self.line_length // (self.w.bpp // 8)

    def put_pixel(self, x: int, y: int, color: int) -> None:
        self.i.address[y * self.w.offset + x] = color

    def put_case(self, col: int, row: int, color: int) -> None:
        for y in range(self.i.case):
            for x in range(self.i.case):
                self.put_pixel(col * self.i.case + x, row * self.i.case + y, color)

    def xwall(self, top: bool, x_s: int, y_s: int, x_e: int, y_e: int, color: int) -> None:
        if top:
            for i in range(self.i.case):
                self.put_pixel(x_s + i, y_s, color)
                self.put_pixel(x_s + i, y_s + 1, color)
        else:
            for i in range(self.i.case):
                self.put_pixel(x_s + i, y_e, color)
                self.put_pixel(x_s + i, y_e - 1, color)

    def ywall(self, left: bool, x_s: int, y_s: int, x_e: int, y_e: int, color: int) -> None:
        if left:
            for i in range(self.i.case):
                self.put_pixel(x_s, y_s + i, color)
                self.put_pixel(x_s + 1, y_s + i, color)
        else:
            for i in range(self.i.case):
                self.put_pixel(x_e, y_s + i, color)
                self.put_pixel(x_e - 1, y_s + i, color)

    def draw_path(self, path: list[tuple[int, int]], color: int) -> None:
        for cell in path:
            self.put_case(cell[0], cell[1], color)

    def draw_wall(self, maze: Maze, cell: Cell, col: int, row: int,
                  pixel: MazeCoord, color: int) -> None:
        if row == 0:
            self.xwall(True, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
            self.xwall(True, pixel.x_start, pixel.y_start + 2, pixel.x_end, pixel.y_end, color)
        if row == maze.height - 1:
            self.xwall(False, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
            self.xwall(False, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end - 2, color)
        if col == 0:
            self.ywall(True, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
            self.ywall(True, pixel.x_start + 2, pixel.y_start, pixel.x_end, pixel.y_end, color)
        if col == maze.width - 1:
            self.ywall(False, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
            self.ywall(False, pixel.x_start - 2, pixel.y_start, pixel.x_end - 2, pixel.y_end, color)
        if cell.N:
            self.xwall(True, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
        if cell.S:
            self.xwall(False, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
        if cell.W:
            self.ywall(True, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
        if cell.E:
            self.ywall(False, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)

    def draw_maze(self, maze: Maze) -> None:
        self.pixel = MazeCoord()
        self.clear_address()
        self.draw_path(maze.path, self.i.purple)
        self.put_case(maze.entry[0], maze.entry[1], self.i.green)
        self.put_case(maze.exit[0], maze.exit[1], self.i.red)
        for row in range(maze.height):
            for col in range(maze.width):
                cell = maze.grid[row][col]
                self.pixel.x_start = col * self.i.case
                self.pixel.y_start = row * self.i.case
                self.pixel.x_end = ((col + 1) * self.i.case) - 1
                self.pixel.y_end = ((row + 1) * self.i.case) - 1
                self.draw_wall(maze, cell, col, row, self.pixel, self.i.white)
                if cell.isftwo:
                    self.put_case(col, row, self.i.white)

    def clear_address(self) -> None:
        total = (self.w.width * self.i.case) * (self.w.height * self.i.case)
        for i in range(total):
            self.i.address[i] = 0

    def close_window(self, param: Any) -> int:
        self.mlx.mlx_destroy_image(self.init, self.i.image)
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


def display_maze(maze: Maze, color: str, path: bool = True, forty_color: str = "\033[30m") -> None:
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


def goodreturn(maze: Maze, maze_WIDTH: int, maze_HEIGHT: int) -> int:
    state: int = 0
    render: Render = Render(maze_WIDTH, maze_HEIGHT, 50)
    render.new_window("A-Maze-Ing")
    render.new_image()

    def catch_key(key: int, param: Any) -> int:
        nonlocal state
        if key == 65307:
            state = 1
            render.close_window(param)
        elif key == 32:
            state = 2
            render.close_window(param)
        return 0

    render.draw_maze(maze)
    render.mlx.mlx_put_image_to_window(render.init, render.w.window, render.i.image, 0, 0)
    render.mlx.mlx_key_hook(render.w.window, catch_key, render.init)
    render.mlx.mlx_hook(render.w.window, 33, 0, render.close_window, None)
    render.mlx.mlx_loop(render.init)
    return state