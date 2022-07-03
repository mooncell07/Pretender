import string
import random

__all__ = ("cbold", "bold", "rbold", "generate_salt")

# some basic terminal text colors, cba making a logger subclass ;)
def bold(statement):
    return f"\033[1m{statement}\033[0m"


def cbold(statement):
    return bold(f"\033[38;5;51m{statement}\033[0m")


def rbold(statement):
    return bold(f"\033[91m{statement}\033[0m")


def generate_salt():
    salt = ""
    for _ in range(16):
        salt += random.choice(string.ascii_letters + string.digits)
    return salt
