from pydantic import BaseModel, Field, model_validator
from typing import ClassVar, Self


class Config(BaseModel):
    """
    Validated configuration model for the maze generator.

    Attributes:
        WIDTH: Maze width in cells (0-1000).
        HEIGHT: Maze height in cells (0-1000).
        ENTRY: Entry point coordinates (x, y).
        EXIT: Exit point coordinates (x, y).
        PERFECT: Whether to generate a perfect maze (no loops).
    """

    WIDTH: int = Field(ge=0, le=1000)
    HEIGHT: int = Field(ge=0, le=1000)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    PERFECT: bool
    OUTPUT: str

    PROTECTED_FILES: ClassVar[set[str]] = {
        "requirements.txt", "config.txt", "Makefile", "a_maze_ing.py"
    }

    @model_validator(mode="after")
    def check_rules(self) -> Self:
        if self.WIDTH <= 3 and self.HEIGHT <= 3:
            raise ValueError("maze is too small to be created")
        if not self.OUTPUT.endswith(".txt"):
            raise ValueError("output must be a .txt file")
        if self.OUTPUT in Config.PROTECTED_FILES:
            raise ValueError(
                f"cannot overwrite protected file: {self.OUTPUT}"
            )
        return self


def parser_conf(data: str) -> dict[str, str]:
    """
    Parse a 'config.txt' file into a key/value dictionary.

    Expected format: KEY=VALUE
    """
    REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT"}
    config: dict[str, str] = {}
    for line in data.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()

    missing = REQUIRED_KEYS - config.keys()
    if missing:
        raise ValueError(f"missing keys: {missing}")
    return config
