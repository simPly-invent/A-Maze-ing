from .generator import *
from .utils import *
from mlx import Mlx
import time
import sys

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




def put_pixel(img_adr, offset, x, y, color):
    img_adr[y * offset + x] = color


def put_topbottom(top, img_adr, offset, size, x_start, y_start, x_end, y_end, color):
    if top:
        for i in range(size):
            put_pixel(img_adr, offset, (x_start + i), y_start, color)
            put_pixel(img_adr, offset, (x_start + i), y_start + 1, color)
    else:
        for i in range(size):
            put_pixel(img_adr, offset, x_start + i, y_end, color)
            put_pixel(img_adr, offset, x_start + i, y_end - 1, color)


def put_side(left, img_adr, offset, size, x_start, y_start, x_end, y_end, color):
    if left:
        for i in range(size):
            put_pixel(img_adr, offset, x_start, y_start + i, color)
            put_pixel(img_adr, offset, x_start + 1, y_start + i, color)
    else:
        for i in range(size):
            put_pixel(img_adr, offset, x_end, y_start + i, color)
            put_pixel(img_adr, offset, x_end - 1, y_start + i, color)


def draw_case(maze, height, width, col, row, img_adr, offset, size, cell, x_start, y_start, x_end, y_end, color):
    if row == 0:
        put_topbottom(True, img_adr, offset, size, x_start, y_start, x_end, y_end, color)
        put_topbottom(True, img_adr, offset, size, x_start, y_start + 2, x_end, y_end, color)
    if row == height - 1:
        put_topbottom(False, img_adr, offset, size, x_start, y_start, x_end, y_end, color)
        put_topbottom(False, img_adr, offset, size, x_start, y_start, x_end, y_end - 2, color)
    if col == 0:
        put_side(True, img_adr, offset, size, x_start, y_start, x_end, y_end, color)
        put_side(True, img_adr, offset, size, x_start + 2, y_start, x_end, y_end, color)
    if col == width - 1:
        put_side(False, img_adr, offset, size, x_start, y_start, x_end, y_end, color)
        put_side(False, img_adr, offset, size, x_start - 2, y_start, x_end - 2, y_end, color)
    if cell.N:
        put_topbottom(True, img_adr, offset, size, x_start, y_start, x_end, y_end, color)
    if cell.S:
        put_topbottom(False, img_adr, offset, size, x_start, y_start, x_end, y_end, color)
    if cell.W:
        put_side(True, img_adr, offset, size, x_start, y_start, x_end, y_end, color)
    if cell.E:
        put_side(False, img_adr, offset, size, x_start, y_start, x_end, y_end, color)


def draw_wall(maze, offset, img_adr, height, width):
    white = 0xFFFFFFFF
    blue = 0xFF0000FF
    green = 0xFF00FF00
    purple = 0xA9A9A9FF
    fortytwo = 0xCCFFFFFF
    size = 50
    total_pixels = (width * 50) * (height * 50)
    for i in range(total_pixels):
        img_adr[i] = 0x00000000
    for col in range(height):
        for row in range(width):
            cell = maze.grid[row][col]
            x_start = col * size
            y_start = row * size
            x_end = ((col + 1) * size) - 1
            y_end = ((row + 1) * size) - 1
            if (col, row) in maze.path:
                for i in range(size):
                    for j in range(size):
                        put_pixel(img_adr, offset, col * size + j, row * size + i, purple)
            if (col, row) == maze.entry:
                for i in range(size):
                    for j in range(size):
                        put_pixel(img_adr, offset, col * size + j, row * size + i, blue)
            if (col, row) == maze.exit:
                for i in range(size):
                    for j in range(size):
                        put_pixel(img_adr, offset, col * size + j, row * size + i, green)
            if cell.isftwo:
                for i in range(size):
                    for j in range(size):
                        put_pixel(img_adr, offset, col * size + j, row * size + i, fortytwo)
            draw_case(maze, height, width, col, row, img_adr, offset, size, cell, x_start, y_start, x_end, y_end, white)
def goodreturn(maze, maze_HEIGHT, maze_WIDTH):
    oui = 0
    def window(maze, maze_HEIGHT, maze_WIDTH):
        mlx = Mlx()
        tile_size = 50
        init = mlx.mlx_init()
        mlx_win = mlx.mlx_new_window(init, maze_WIDTH * tile_size, maze_HEIGHT * tile_size + 150, "a-maze-ing")
        mlx_img = mlx.mlx_new_image(init, maze_WIDTH * tile_size, maze_HEIGHT * tile_size)
        img_adr, bpp, line_length, endian = mlx.mlx_get_data_addr(mlx_img)
        img_adr = img_adr.cast('I')
        def win_close(key, param):
            print(key)
            nonlocal oui
            if key == 65307:
                oui = 1
                mlx.mlx_destroy_image(init, mlx_img)
                mlx.mlx_destroy_window(init, mlx_win)
                mlx.mlx_loop_exit(init)
            elif key == 32:
                oui = 2
                print("Relance du labyrinthe...")
                mlx.mlx_destroy_image(init, mlx_img)
                mlx.mlx_destroy_window(init, mlx_win)
                mlx.mlx_loop_exit(init) 

        def print_coor(x, y, param):    
            tile_x = x // 50
            tile_y = y // 50
            print(f"({tile_x}, {tile_y})")

        lines = [
            "--- COMMANDES ---",
            "ESC : Quitter le programme",
            "SPACE : Lancer une nouvelle generation"
        ]

        for i, text in enumerate(lines):
            text_offset = (len(text) * 7) // 2 
            mlx.mlx_string_put(init, mlx_win, maze_WIDTH , maze_HEIGHT * tile_size + 50 + (i * 30), 0xFFFFFF, text)

        offset = line_length // (bpp // 8)
        draw_wall(maze, offset, img_adr, maze_HEIGHT, maze_WIDTH)
        mlx.mlx_put_image_to_window(init, mlx_win, mlx_img, 0, 0)
        mlx.mlx_key_hook(mlx_win, win_close, init)
        mlx.mlx_hook(mlx_win, 6, 1 << 6, print_coor, None)
        mlx.mlx_loop(init)
    window(maze, maze_HEIGHT, maze_WIDTH)
    return oui