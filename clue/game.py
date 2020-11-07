from typing import List, Tuple, Optional, Set, Union
from pandas import DataFrame
from pysat.solvers import Maplesat as Solver
from itertools import combinations
from clue.card import Card, Character, Room, Weapon, Case


class Game:
    def __init__(self):
        self.sat = Solver()
        self.initial_clauses()

    def hand(self, player: Character, cards: Set[Card]):
        """
        add knowledge of my hand
        """

        for card in cards:
            atom = Card.to_atomic_sentence(card, player)
            self.sat.add_clause([atom])

    def test(self, card: Card, place: Card) -> Optional[bool]:
        """
        if its solvable with this assumption, ensure it can't
        be disproven by the inverse of the assumption
        """

        literal = Card.to_atomic_sentence(card, place)
        a = self.sat.solve(assumptions=[literal])

        if not a:
            return a

        b = self.sat.solve(assumptions=[-literal])

        if not b:
            return a

        return None

    def suggest(
        self,
        suggester: Character,
        suspect: Character,
        weapon: Weapon,
        room: Room,
        refuter: Optional[Character] = None,
        card_shown: Optional[Card] = None,
    ):
        pass

    def accuse(
        self,
        accuser: Character,
        suspect: Character,
        weapon: Weapon,
        room: Room,
        is_correct: bool,
    ):
        pass

    def matrix(self) -> List[List[Optional[bool]]]:
        """
        game state in matrix form
        """

        matrix = []

        for card in Card.deck():
            row = []
            for place in Card.places():
                result = self.test(card, place)
                row.append(result)
            matrix.append(row)

        return matrix

    def notepad(self) -> DataFrame:
        """
        pretty print our understanding of game state
        """

        df = DataFrame.from_records(
            self.matrix(),
            columns=[p.name.lower() for p in Card.places()],
            index=[c.name.lower() for c in Card.deck()],
        )

        def fmt(x):
            return {None: "-", True: 1, False: 0}[x]

        return df.applymap(fmt)

    def initial_clauses(self):
        """
        establish base logic for the game. things that all players know
        before gameplay even starts
        """

        file = Case.FILE
        clause = set()

        """
        each card in at least one place
        """

        for card in Card.deck():
            clause = []
            for place in Card.places():
                clause.append(Card.to_atomic_sentence(card, place))
            self.sat.add_clause(clause)

        """
        if card is in one place, it can't be in another place
        """

        for card in Card.deck():
            for a, b in combinations(Card.places(), 2):
                clause = [
                    -Card.to_atomic_sentence(card, a),
                    -Card.to_atomic_sentence(card, b),
                ]
                self.sat.add_clause(clause)

        """
        at least one card of each category in case file
        """

        for category in {Weapon, Room, Character}:
            clause = [Card.to_atomic_sentence(i, file) for i in category]
            self.sat.add_clause(clause)

        """
        no two cards in each category are in case file
        """

        for category in {Weapon, Room, Character}:
            for a, b in combinations(category, 2):
                clause = [
                    -Card.to_atomic_sentence(a, file),
                    -Card.to_atomic_sentence(b, file),
                ]
                self.sat.add_clause(clause)