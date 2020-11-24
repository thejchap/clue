from typing import List
from clue import service, sat

SERVICE = service.GameService()


def run(args: List[str]) -> str:
    """
    run from command line
    """

    name = args[1]
    result = ""

    if name == "notepad":
        game = SERVICE.show(args[2])

        if not game:
            return result

        result = sat.notepad(game.players, game.cnf)

    return result