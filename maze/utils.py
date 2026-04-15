RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


def check_forty_two_length(height: int, width: int) -> bool:
    if height >= 5 and width >= 7:
        return True
    return False
