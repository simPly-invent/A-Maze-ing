from .generator import *
from .utils import *
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