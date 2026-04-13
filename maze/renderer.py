from .generator import *
from .utils import *
from mlx import Mlx
import time
import sys


class Window:
    def __init__(self, width: int, height: int):
        self.window = None
        self.bpp = 0
        self.offset = 0
        if height < 0:
            self.height = 0
        else:
            self.height = height
        if width < 0:
            self.width = 0
        else:
            self.width = width


class Image:
    def __init__(self, case: int):
        self.image = None
        self.address = None
        if (case < 0):
            self.case = 32
        else:
            self.case = case
        self.red = 0xFFFF0000
        self.green = 0xFF00FF00
        self.purple = 0xA9A9A9FF
        self.grey = 0xCCFFFFFF
        self.white = 0xFFFFFFFF


class MazeCoord:
    def __init__(self):
        self.x = 0
        self.x_start = 0
        self.x_end = 0
        self.y = 0
        self.y_start = 0
        self.y_end = 0


class Render:
    def __init__(self, width, height, case):
        self.mlx = Mlx()
        self.init = self.mlx.mlx_init()
        self.w = Window(width, height)
        self.i = Image(case)

    def new_window(self, name: str):
        self.w.window = self.mlx.mlx_new_window(self.init, self.w.width * self.i.case, self.w.height * self.i.case + 150, name)

    def new_image(self):
        self.i.image = self.mlx.mlx_new_image(self.init, self.w.width * self.i.case, self.w.height * self.i.case)
        self.i.address, self.w.bpp, self.line_length, self.endian = self.mlx.mlx_get_data_addr(self.i.image)
        self.i.address = self.i.address.cast('I')
        self.w.offset = self.line_length // (self.w.bpp // 8)

    def put_pixel(self, x, y, color):
        self.i.address[y * self.w.offset + x] = color

    def put_case(self, col, row, color):
        for y in range(self.i.case):
            for x in range(self.i.case):
                self.put_pixel(col * self.i.case + x, row * self.i.case + y, color)

    def xwall(self, top, x_start, y_start, x_end, y_end, color):
        if top:
            for i in range(self.i.case):
                self.put_pixel(x_start + i, y_start, color)
                self.put_pixel(x_start + i, y_start + 1, color)
        else:
            for i in range(self.i.case):
                self.put_pixel(x_start + i, y_end, color)
                self.put_pixel(x_start + i, y_end - 1, color)

    def ywall(self, left, x_start, y_start, x_end, y_end, color):
        if left:
            for i in range(self.i.case):
                self.put_pixel(x_start, y_start + i, color)
                self.put_pixel(x_start + 1, y_start + i, color)
        else:
            for i in range(self.i.case):
                self.put_pixel(x_end, y_start + i, color)
                self.put_pixel(x_end - 1, y_start + i, color)

    def draw_path(self, path, color):
        for cell in path:
            self.put_case(cell[0], cell[1], color)

    def draw_wall(self, maze, cell, col, row, pixel, color):
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

    def draw_maze(self, maze):
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

    def clear_address(self):
        total = (self.w.width * self.i.case) * (self.w.height * self.i.case)
        for i in range(total):
            self.i.address[i] = 0

    def close_window(self, param):
        self.mlx.mlx_destroy_image(self.init, self.i.image)
        self.mlx.mlx_destroy_window(self.init, self.w.window)
        self.mlx.mlx_loop_exit(self.init)

def intro_animation(color):
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


def display_maze(maze, color):
    """
    Affiche le labyrinthe dans le terminal.

    Gère :
    → les murs (│ ─ ┼ etc)
    → l'entrée (o jaune)
    → la sortie (o violet)
    → le chemin BFS (.)

    Bonus :
    → si generate == False → case pas encore générée

    En gros :
    → c'est uniquement de l'affichage, aucune logique de labyrinthe
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
                line1 += "███"
            elif (x, y) in maze.path:
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

        line2 = line2[:-1] + f"│"

        print(line1)

        if y < height - 1:
            print(line2)

    print(COLOR_MAZE + "└" + "───┴" * (width - 1) + "───┘" + RESET)


# def put_pixel(image, window, x, y, color):
#     image.address[y * window.offset + x] = color
#
#
# def put_case(maze, window, image, col, row, color):
#     for y in range(image.case):
#         for x in range(image.case):
#             put_pixel(image, window, col * image.case + x, row * image.case + y, color)
#
#
# def put_xwall(top, window, image, x_start, y_start, x_end, y_end, color):
#     if top:
#         for i in range(image.case):
#             put_pixel(image, window, (x_start + i), y_start, color)
#             put_pixel(image, window, (x_start + i), y_start + 1, color)
#     else:
#         for i in range(image.case):
#             put_pixel(image, window, x_start + i, y_end, color)
#             put_pixel(image, window, x_start + i, y_end - 1, color)
#
#
# def put_ywall(left, window, image, x_start, y_start, x_end, y_end, color):
#     if left:
#         for i in range(image.case):
#             put_pixel(image, window, x_start, y_start + i, color)
#             put_pixel(image, window, x_start + 1, y_start + i, color)
#     else:
#         for i in range(image.case):
#             put_pixel(image, window, x_end, y_start + i, color)
#             put_pixel(image, window, x_end - 1, y_start + i, color)
#
#
# def draw_path(maze, window, image, path, color):
#     for cell in path:
#         put_case(maze, window, image, cell[0], cell[1], color)
#
#
# def draw_wall(maze, window, image, col, row, cell, pixel, color):
#     if row == 0:
#         put_xwall(True, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#         put_xwall(True, window, image, pixel.x_start, pixel.y_start + 2, pixel.x_end, pixel.y_end, color)
#     if row == maze.height - 1:
#         put_xwall(False, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#         put_xwall(False, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end - 2, color)
#     if col == 0:
#         put_ywall(True, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#         put_ywall(True, window, image, pixel.x_start + 2, pixel.y_start, pixel.x_end, pixel.y_end, color)
#     if col == maze.width - 1:
#         put_ywall(False, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#         put_ywall(False, window, image, pixel.x_start - 2, pixel.y_start, pixel.x_end - 2, pixel.y_end, color)
#     if cell.N:
#         put_xwall(True, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#     if cell.S:
#         put_xwall(False, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#     if cell.W:
#         put_ywall(True, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#     if cell.E:
#         put_ywall(False, window, image, pixel.x_start, pixel.y_start, pixel.x_end, pixel.y_end, color)
#
#
# def draw_maze(maze, window, image, render):
#     pixel = MazeCoord()
#     render.clear_address()
#     draw_path(maze, window, image, maze.path, image.purple)
#     put_case(maze, window, image, maze.entry[0], maze.entry[1], image.green)
#     put_case(maze, window, image, maze.exit[0], maze.exit[1], image.red)
#     for row in range(maze.height):
#         for col in range(maze.width):
#             cell = maze.grid[row][col]
#             pixel.x_start = col * image.case
#             pixel.y_start = row * image.case
#             pixel.x_end = ((col + 1) * image.case) - 1
#             pixel.y_end = ((row + 1) * image.case) - 1
#             draw_wall(maze, window, image, col, row, cell, pixel, image.white)
#             if cell.isftwo:
#                 put_case(maze, window, image, col, row, image.white)


def goodreturn(maze, maze_WIDTH, maze_HEIGHT):
    state = 0

    render = Render(maze_WIDTH, maze_HEIGHT, 50)
    render.new_window("A-Maze-Ing")
    render.new_image()


    def catch_key(key, param):
        print(key)
        nonlocal state
        if key == 65307:
            state = 1
            render.close_window(param)
        elif key == 32:
            state = 2
            render.close_window(param)

    lines = [
        "--- COMMAND ---",
        "ESC : Exit program",
        "SPACE : Generate a new maze"
    ]

    # for j, text in enumerate(lines):
    #     text_offset = (len(text) * 7) // 2
    #     mlx.mlx_string_put(render.init, render.w.window, render.w.width, render.w.height * render.i.case + 50 + (j * 30), 0xFFFFFF, text)

    # draw_maze(maze, render.w, render.i, render)
    render.draw_maze(maze)
    render.mlx.mlx_put_image_to_window(render.init, render.w.window, render.i.image, 0, 0)
    render.mlx.mlx_key_hook(render.w.window, catch_key, render.init)
    render.mlx.mlx_hook(render.w.window, 33, 0, render.close_window, None)
    render.mlx.mlx_loop(render.init)
    return state
