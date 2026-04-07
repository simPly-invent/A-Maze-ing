from pydantic import BaseModel, Field, model_validator

class Config(BaseModel):
    WIDTH: int = Field(ge=0, le=1000)
    HEIGHT: int = Field(ge=0, le=1000)
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    PERFECT: bool

    @model_validator(mode="after")
    def check_rules(self):
        if self.WIDTH == 3 and self.HEIGHT == 3:
            raise ValueError("maze to small to be create")
        return self


def parser_conf(data):
    """
    Parse le fichier config.txt.

    Format attendu :
    KEY=VALUE

    Ignore :
    → lignes vides
    → commentaires (#)

    Retour :
    → dictionnaire avec les configs

    En gros :
    → permet de config le labyrinthe facilement
    """
    config_dico = {}
    for line in data.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config_dico[key] = value
    return config_dico