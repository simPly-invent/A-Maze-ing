from __future__ import annotations

import sys
from typing import Callable, Any, cast

from pydantic import ValidationError

from maze import (
    RED, GREEN, YELLOW, MAGENTA,
    Config, Maze, growing_tree, dfs, bfs,
    random_breaker, initforty_two, check_forty_two_length,
    convert_maze_output, display_maze, goodreturn,
    parser_conf, intro_animation
)


class CheckErrorLocation(Exception):
    pass


_COLORS: dict[str, str] = {
    "RED": RED,
    "GREEN": GREEN,
    "YELLOW": YELLOW,
    "MAGENTA": MAGENTA,
}

_COLOR_PROMPT: str = (
    "Which color do you want?\n"
    "-> \033[31mRED\033[0m\n"
    "-> \033[32mGREEN\033[0m\n"
    "-> \033[33mYELLOW\033[0m\n"
    "-> \033[35mMAGENTA\033[0m\n: "
)


class Menu:
    """Interactive text menu for configuring and launching mazes."""

    def __init__(self,
                 maze_conf: Config,
                 perfect: bool,
                 color: str,
                 output: str) -> None:
        self.maze_conf = maze_conf
        self.color = color
        self.i = 30
        self.forty_color = f"\033[{self.i}m"
        self.perfect = perfect
        self.output = output

    def growing_tree_menu(self, type_display: str, init_forty: str) -> Maze:
        """Build a maze using the Growing Tree algorithm."""
        maze = Maze(
            self.maze_conf.HEIGHT,
            self.maze_conf.WIDTH,
            self.maze_conf.ENTRY,
            self.maze_conf.EXIT,
        )
        if init_forty:
            initforty_two(maze)

        while True:
            try:
                if type_display == "test":
                    x, y = 1, 1
                else:
                    msg = "Starting generation from (x,y)?\n"
                    raw_input = input(msg)
                    coords = list(map(int, raw_input.split(",")))
                    x, y = coords[0], coords[1]
                if x < 0 or y < 0 or x >= maze.width or y >= maze.height:
                    raise ValueError("out of the range")
            except (ValueError, IndexError) as e:
                print(e)
            else:
                break

        growing_tree(maze, y, x, self.color, type_display)
        if not self.perfect:
            random_breaker(maze, 0.10)
        bfs(maze)
        return maze

    def dfs_menu(self, type_display: str, init_forty: str) -> Maze:
        """Build a maze using the Depth-First Search algorithm."""
        maze = Maze(
            self.maze_conf.HEIGHT,
            self.maze_conf.WIDTH,
            self.maze_conf.ENTRY,
            self.maze_conf.EXIT,
        )
        if init_forty:
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

    def run(self) -> None:
        """Start the interactive main menu loop."""
        algo: Callable[[str, str], Maze] = self.dfs_menu
        render_label: str = "Ascii render"
        rl_render: str = "ascii"
        maze: Maze | None = None
        path: bool = True
        intro_animation(self.color)

        while True:
            if self.i == 35:
                self.i = 30
            self.forty_color = f"\033[{self.i}m"
            algo_label = algo.__name__.replace("_", " ")
            print(
                " ------------\n"
                "| board menu |\n"
                "  ------------\n"
                f"State      : {'perfect' if self.perfect else 'not perfect'}\n"
                f"Dimensions : {self.maze_conf.HEIGHT} "
                f"x {self.maze_conf.WIDTH}\n"
                f"Algorithm  : {algo_label}\n"
                f"Render     : {render_label}\n"
                " ---------------------------\n"
                "| Menu, what do you want?   |\n"
                " ---------------------------"
            )
            user = input(
                "\n 1) Launch maze generation\n"
                " 2) Switch render\n"
                " 3) Switch algorithm\n"
                " 4) Toggle perfect / not perfect\n"
                " 5) Change maze dimensions\n"
                " 6) Change maze color\n"
                "       | 42) change 42 color\n"
                " 7) show path or not\n"
                " 8) exit from the program\n"
                ": "
            )

            if user == "1":
                while True:
                    initforty = check_forty_two_length(
                        self.maze_conf.HEIGHT, self.maze_conf.WIDTH
                    )
                    temp_maze = algo("test", initforty)
                    ex, ey = temp_maze.entry
                    sx, sy = temp_maze.exit
                    try:
                        if not temp_maze.grid[ey][ex].isbreakable:
                            raise CheckErrorLocation("entry in 42 logo")
                        if not temp_maze.grid[sy][sx].isbreakable:
                            raise CheckErrorLocation("exit in 42 logo")
                    except CheckErrorLocation as e:
                        print(e)
                        break

                    maze = algo(rl_render, initforty)
                    convert_maze_output(maze, self.output)
                    if rl_render == "ascii":
                        print("\033c")
                        display_maze(maze, self.color, path)
                        if not initforty:
                            print("the 42 cannot be contain in maze")
                        input("\nPress Enter to return to the menu...")
                        break
                    else:
                        display_maze(maze, self.color, path)
                        res = goodreturn(maze)
                        if res != 2:
                            break

            elif user == "2":
                if rl_render == "ascii":
                    render_label, rl_render = "Mlx render", "mlx"
                else:
                    render_label, rl_render = "Ascii render", "ascii"
                print("\033c")

            elif user == "3":
                if algo == self.dfs_menu:
                    algo = self.growing_tree_menu
                else:
                    algo = self.dfs_menu
                print("\033c")

            elif user == "4":
                self.perfect = not self.perfect
                print("\033c")

            elif user == "5":
                while True:
                    try:
                        dims = input("Enter dims as 'height,width':\n: ")
                        h_str, w_str = dims.split(",")
                        h, w = int(h_str), int(w_str)
                        Config(
                            HEIGHT=h, WIDTH=w,
                            ENTRY=self.maze_conf.ENTRY,
                            EXIT=self.maze_conf.EXIT,
                            OUTPUT=self.output,
                            PERFECT=self.perfect
                        )
                        self.maze_conf.HEIGHT, self.maze_conf.WIDTH = h, w
                    except (ValueError, ValidationError, IndexError) as e:
                        print(e)
                    else:
                        break
                print("\033c")

            elif user == "6":
                if maze is None:
                    print("No maze has been generated yet.")
                    continue
                self.change_color()
                print("\033c")
                display_maze(maze, self.color, path, self.forty_color)

            elif user == "7":
                if maze is None:
                    print("error : create maze before path toggle")
                else:
                    path = not path
                    print("\033c")
                    display_maze(maze, self.color, path, self.forty_color)
            elif user == "42":
                if maze is None:
                    print("error : create maze before changing 42 color")
                else:
                    self.i += 1
                    self.forty_color = f"\033[{self.i}m"
                    print("\033c")
                    display_maze(maze, self.color, path, self.forty_color)
            elif user == "8":
                print("\033c\nGoodbye :)")
                break
            else:
                print("Goodbye :)")
                break


if __name__ == "__main__":
    try:
        with open("config.txt", "r") as f:
            raw_data = f.read()
        config_data = parser_conf(raw_data)
        m_conf = Config(
            WIDTH=int(config_data["WIDTH"]),
            HEIGHT=int(config_data["HEIGHT"]),
            ENTRY=cast(Any, tuple(
                map(int, config_data["ENTRY"].split(","))
            )),
            EXIT=cast(Any, tuple(
                map(int, config_data["EXIT"].split(","))
            )),
            OUTPUT=str(config_data["OUTPUT_FILE"]),
            PERFECT=config_data["PERFECT"].lower() == "true"
        )
        menu_obj = Menu(m_conf, m_conf.PERFECT, RED, m_conf.OUTPUT)
        menu_obj.run()

    except FileNotFoundError:
        print("Error: config.txt not found.")
    except ValidationError as exc:
        for err in exc.errors():
            fld = err["loc"][0] if err["loc"] else "Config"
            print(f"{fld}: {err['msg']}")
    except (ValueError, CheckErrorLocation) as e:
        print(f"\nError: {e}")
    except KeyboardInterrupt:
        print("\nGoodbye !")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
