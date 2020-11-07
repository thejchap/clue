from clue.game import Game
from clue.card import Card, Character, Case, Room, Weapon


def main():
    game = Game()
    game.hand(Character.SCARLETT, {Room.KITCHEN, Weapon.DAGGER})
    game.sat.add_clause(
        {-Card.to_atomic_sentence(Weapon.CANDLESTICK, Character.SCARLETT)}
    )

    print(game.notepad())


if __name__ == "__main__":
    main()