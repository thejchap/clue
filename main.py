from pprint import pprint
from clue.game import Game
from clue.card import Card, Character, Case, Room, Weapon


def main():
    game = Game(players=list(Character), me=Character.SCARLETT)
    game.hand({Room.KITCHEN, Weapon.DAGGER})

    game.suggest(
        Character.SCARLETT,
        Character.WHITE,
        Weapon.PIPE,
        Room.HALL,
        Character.PLUM,
        False,
    )

    print(game.notepad())


if __name__ == "__main__":
    main()