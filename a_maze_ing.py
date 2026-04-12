from maze import *


class Menu:
    def __init__(self, maze_conf, perfect, color):
        self.maze_conf = maze_conf
        self.color = color
        self.perfect = perfect
    

    def growing_tree_menu(self, type_display) -> Maze:
        maze_test = Maze(self.maze_conf.HEIGHT, self.maze_conf.WIDTH, self.maze_conf.ENTRY, self.maze_conf.EXIT)
        initforty_two(maze_test)
        coords = list(map(int, input("starting generation from (x,y) ?\n").split(",")))
        x, y = coords
        growing_tree(maze_test, y, x, self.color, type_display)
        if not self.perfect:
            random_breaker(maze_test, 0.10)
        bfs(maze_test)
        return maze_test
    
    def dfs_menu(self, type_display) -> Maze:
        maze_test = Maze(self.maze_conf.HEIGHT, self.maze_conf.WIDTH, self.maze_conf.ENTRY, self.maze_conf.EXIT)
        initforty_two(maze_test)
        dfs(maze_test, color, type_display)
        if not self.perfect:
            random_breaker(maze_test, 0.10)
        bfs(maze_test)
        return maze_test

    def change_color(self):pass

    


if __name__ == "__main__":
    r = open("config.txt", "r")
    config = parser_conf(r.read())
    try:
        maze_conf = Config(
            WIDTH=int(config["WIDTH"]),
            HEIGHT=int(config["HEIGHT"]),
            ENTRY=tuple(map(int, config["ENTRY"].split(","))),
            EXIT=tuple(map(int, config["EXIT"].split(","))),
            PERFECT=config["PERFECT"].lower() == "true"
        )
    except ValidationError as e:
        print(e)
        exit(1)

    try:
        perfect = maze_conf.PERFECT
        color = RED
        m = Menu(maze_conf, perfect, color)
        intro_animation(color)
        algo = m.dfs_menu
        Maze_render = "Ascii render"
        rl_render = "ascii"
        maze = None
        type_display = "color"
        while True:
            print(" ------------")
            print("| board menu |")
            print("  ------------")
            print(f"State of the maze: {'perfect' if m.perfect else 'not perfect'}\nglobal dimensions = {m.maze_conf.HEIGHT}, {m.maze_conf.WIDTH}\nAlgo : {algo.__name__.replace("_", " ")}\nRender : {Maze_render}")
            print(" --------------------------- ")
            print("| Menu, do what you want  ? |")
            print(" --------------------------- ")
            user = input(f"\n\n 1) launch the maze generation\n 2) switch render \n 3) switch Algoritms \n 4) switch perfect/not perfect\n 5) change maze dimension\n 6) change the color of the maze \n")
            if not maze and user == "6":
                print("no maze can be found")
                continue
            if user == "1":
                while True:
                    maze = algo(rl_render)
                    if rl_render == "ascii":
                        print("\033c")
                        display_maze(maze, color)
                        input("\nPressez Entrer pour afficher le menu...")
                        break 
                    else:
                        num = goodreturn(maze, m.maze_conf.HEIGHT, m.maze_conf.WIDTH)
                        if num == 1:
                            break
                        elif num == 2:
                            continue 
                        else:
                            break
                continue
            elif user == "2":
                if rl_render == "ascii":
                    Maze_render = "Mlx render"
                    rl_render = "mlx"
                else:
                    Maze_render = "Ascii render"
                    rl_render = "ascii"
                print("\033c")
                continue
            elif user == "3":
                if algo == m.growing_tree_menu:
                    algo = m.dfs_menu
                else:
                    algo = m.growing_tree_menu
                print("\033c")
                continue
            elif user == "4":
                type_display = "perfect"
                m.perfect = not m.perfect
                print("\033c")
                continue
            elif user == "5":
                user_dimension = input("'height,width' <- format without space please\n:")
                m.maze_conf.HEIGHT, m.maze_conf.WIDTH = map(int, user_dimension.split(","))
                print("\033c")
                continue
            elif user == "6":
                type_display = "color"
                print("\033c")
                color = input("Which color you want ? \n\
-> \033[31mRED\033[0m\n\
-> \033[32mGREEN\033[0m\n\
-> \033[33mYELLOW\033[0m\n->\
 \033[35mMAGENTA\033[0m\n: ")
                color = color.upper()
                if color == "GREEN":
                    color = GREEN
                if color == "RED":
                    color = RED
                if color == "YELLOW":
                    color = YELLOW
                if color == "MAGENTA":
                    color = MAGENTA
                print("\033c")
                display_maze(maze, color)
                continue
            else:
                print("goodbye :(")
                break
    except (KeyboardInterrupt, ValueError) as e:
        print(f"\nan error occurred: {e}")
