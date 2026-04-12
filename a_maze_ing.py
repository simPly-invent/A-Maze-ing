from __future__ import annotations

import sys
from typing import Callable

from pydantic import ValidationError

from maze import *


_COLORS: dict[str, str] = {
    "RED": RED,
    "GREEN": GREEN,
    "YELLOW": YELLOW,
    "MAGENTA": MAGENTA,
}

_COLOR_PROMPT = (
    "Which color do you want?\n"
    "-> \033[31mRED\033[0m\n"
    "-> \033[32mGREEN\033[0m\n"
    "-> \033[33mYELLOW\033[0m\n"
    "-> \033[35mMAGENTA\033[0m\n: "
)


class Menu:
    """
    Interactive text menu for configuring and launching maze generation.

    Attributes:
        maze_conf: Validated maze configuration (dimensions, entry, exit…).
        color: Current ANSI color code used by the renderer.
        perfect: Whether the generated maze should be perfect (loop-free).
    """

    def __init__(self, maze_conf: Config, perfect: bool, color: str) -> None:
        self.maze_conf = maze_conf
        self.color = color
        self.perfect = perfect

    # ------------------------------------------------------------------
    # Generation methods
    # ------------------------------------------------------------------

    def growing_tree_menu(self, type_display: str) -> Maze:
        """
        Build a maze using the Growing Tree algorithm.

        Prompts the user for a starting coordinate, runs the generator,
        optionally breaks extra walls, then solves the maze with BFS.

        Args:
            type_display: Rendering mode forwarded to the generator
                          ("ascii" enables step-by-step animation).

        Returns:
            The fully generated and solved Maze object.
        """
        maze = Maze(
            self.maze_conf.HEIGHT,
            self.maze_conf.WIDTH,
            self.maze_conf.ENTRY,
            self.maze_conf.EXIT,
        )
        initforty_two(maze)
        coords = list(map(int, input("Starting generation from (x,y)?\n").split(",")))
        x, y = coords
        growing_tree(maze, y, x, self.color, type_display)
        if not self.perfect:
            random_breaker(maze, 0.10)
        bfs(maze)
        return maze

    def dfs_menu(self, type_display: str) -> Maze:
        """
        Build a maze using the Depth-First Search algorithm.

        Args:
            type_display: Rendering mode forwarded to the generator
                          ("ascii" enables step-by-step animation).

        Returns:
            The fully generated and solved Maze object.
        """
        maze = Maze(
            self.maze_conf.HEIGHT,
            self.maze_conf.WIDTH,
            self.maze_conf.ENTRY,
            self.maze_conf.EXIT,
        )
        initforty_two(maze)
        dfs(maze, self.color, type_display)
        if not self.perfect:
            random_breaker(maze, 0.10)
        bfs(maze)
        return maze

    def change_color(self) -> None:
        """Prompt the user to pick a new display color."""
        choice = input(_COLOR_PROMPT).upper()
        self.color = _COLORS.get(choice, self.color)

    # ------------------------------------------------------------------
    # Main event loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """
        Start the interactive main menu loop.

        Presents options to the user and dispatches actions until the
        user chooses to quit or an unrecoverable error occurs.
        """
        algo: Callable[[str], Maze] = self.dfs_menu
        render_label = "Ascii render"
        rl_render = "ascii"
        maze: Maze | None = None

        intro_animation(self.color)

        while True:
            algo_label = algo.__name__.replace("_", " ")
            print(
                " ------------\n"
                "| board menu |\n"
                "  ------------\n"
                f"State      : {'perfect' if self.perfect else 'not perfect'}\n"
                f"Dimensions : {self.maze_conf.HEIGHT} x {self.maze_conf.WIDTH}\n"
                f"Algorithm  : {algo_label}\n"
                f"Render     : {render_label}\n"
                " ---------------------------\n"
                "| Menu, what do you want?  |\n"
                " ---------------------------"
            )
            user = input(
                "\n 1) Launch maze generation\n"
                " 2) Switch render\n"
                " 3) Switch algorithm\n"
                " 4) Toggle perfect / not perfect\n"
                " 5) Change maze dimensions\n"
                " 6) Change maze color\n"
                ": "
                )

            if user == "1":
                while True:
                    maze = algo(rl_render)
                    convert_maze_output(maze)
                    if rl_render == "ascii":
                        print("\033c")
                        display_maze(maze, self.color)
                        input("\nPress Enter to return to the menu...")
                        break
                    else:
                        result = goodreturn(maze, self.maze_conf.HEIGHT, self.maze_conf.WIDTH)
                        if result != 2:
                            break

            elif user == "2":
                if rl_render == "ascii":
                    render_label = "Mlx render"
                    rl_render = "mlx"
                else:
                    render_label = "Ascii render"
                    rl_render = "ascii"
                print("\033c")

            elif user == "3":
                algo = self.dfs_menu if algo == self.growing_tree_menu else self.growing_tree_menu
                print("\033c")

            elif user == "4":
                self.perfect = not self.perfect
                print("\033c")

            elif user == "5":
                dims = input("Enter dimensions as 'height,width' (no spaces):\n: ")
                self.maze_conf.HEIGHT, self.maze_conf.WIDTH = map(int, dims.split(","))
                print("\033c")

            elif user == "6":
                if maze is None:
                    print("No maze has been generated yet.")
                    continue
                self.change_color()
                print("\033c")
                display_maze(maze, self.color)

            else:
                print("Goodbye :)")
                break


if __name__ == "__main__":
    with open("config.txt", "r") as f:
        raw = f.read()

    config = parser_conf(raw)

    try:
        maze_conf = Config(
            WIDTH=int(config["WIDTH"]),
            HEIGHT=int(config["HEIGHT"]),
            ENTRY=tuple(map(int, config["ENTRY"].split(","))),
            EXIT=tuple(map(int, config["EXIT"].split(","))),
            PERFECT=config["PERFECT"].lower() == "true",
        )
    except ValidationError as exc:
        print(exc)
        sys.exit(1)

    try:
        menu = Menu(maze_conf, maze_conf.PERFECT, RED)
        menu.run()
    except (KeyboardInterrupt, ValueError) as exc:
        print(f"\nAn error occurred: {exc}")
        sys.exit(1)