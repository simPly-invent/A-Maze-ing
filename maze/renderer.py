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





def window(maze, maze_HEIGHT, maze_WIDTH):
    def win_close(key, *param):
        print(key)
        if key == 65307:
            mlx.mlx_loop_exit(param[0])

    def put_pixel(img_adr, offset, x, y, color):
        img_adr[y * offset + x] = color


    def put_case(maze, width, height, img_adr, offset, color, tile):
        blue = 0xFF0000FF
        green = 0xFF00FF00
        white = 0xFFFFFFFF
        wall = 2
        for col in range(height):
            for row in range(width):
                cell = maze.grid[row][col]
                for y in range(tile):
                    for x in range(tile):
                        if (col, row) == maze.entry:
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), blue)
                        elif (col, row) == maze.exit:
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), green)
                        elif (col, row) in maze.path:
                            color = 0xA9A9A9FF
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), color)
                        if (cell.N and y < wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)
                        elif (cell.S and y >= tile - wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)
                        if (cell.E and x >= tile - wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)
                        elif (cell.W and x < wall):
                            put_pixel(img_adr, offset, (col * tile + x), (row * tile + y), white)
                    


    mlx = Mlx()

    tile_size = 50

    init = mlx.mlx_init()

    mlx_win = mlx.mlx_new_window(init, maze_WIDTH * tile_size, maze_HEIGHT * tile_size, "a-maze-ing")
    mlx_img = mlx.mlx_new_image(init, maze_WIDTH * tile_size, maze_HEIGHT * tile_size)
    img_adr, bpp, line_length, endian = mlx.mlx_get_data_addr(mlx_img)
    img_adr = img_adr.cast('I')
    offset = line_length // (bpp // 8)
    put_case(maze, maze_WIDTH, maze_HEIGHT, img_adr, offset, 0, tile_size)
    mlx.mlx_put_image_to_window(init, mlx_win, mlx_img, 0, 0)
    mlx.mlx_key_hook(mlx_win, win_close, init)
    mlx.mlx_loop(init)