from typing import List, Tuple, Optional, Set, Union
from itertools import combinations, cycle
from dataclasses import dataclass, field
from pandas import DataFrame
from pysat.solvers import Maplesat as Solver
from clue.card import Card, Character, Room, Weapon, Case


@dataclass
class Game:
    me: Character
    players: List[Character] = field(default_factory=list)
    sat: Solver = None

    def __post_init__(self):
        """
        initialization. set up our solver with stuff that all players
        take for granted
        """

        self.sat = Solver(bootstrap_with=self.initial_clauses())

    def hand(self, cards: Set[Card]):
        """
        add knowledge of my hand
        """

        for card in Card.deck():
            atom = Card.to_atomic_sentence(card, self.me)
            atom = atom if card in cards else -atom
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
        """
        a players turn. record who suggested what murder, and who, if anyone,
        refuted it. if it was our turn and we were shown a card, we can take
        that into account too
        """

        if refuter:
            """
            somebody showed one of the 3 cards
            """

            if card_shown:
                """
                i was the suggester so i got to see the card
                """

                sentence = Card.to_atomic_sentence(card_shown, refuter)
                self.sat.add_clause([sentence])
            else:
                """
                refuter has one of the 3 cards
                """

                clause = []
                for card in [suspect, weapon, room]:
                    sentence = Card.to_atomic_sentence(card, refuter)
                    clause.append(sentence)
                self.sat.add_clause(clause)

            """
            everybody between suggester and refuter has none of the cards
            """

            on = False

            for player in cycle(self.players):
                if player == suggester:
                    if on:
                        break
                    else:
                        on = True
                        continue

                if player == refuter:
                    break

                if on:
                    for card in [suspect, weapon, room]:
                        sentence = -Card.to_atomic_sentence(card, player)
                        self.sat.add_clause([sentence])
        else:
            """
            we learned that nobody has any of these cards.
            i might, if i was bluffing or whateve
            """

            for player in self.players:
                if player == suggester:
                    continue

                for card in [suspect, weapon, room]:
                    sentence = -Card.to_atomic_sentence(card, player)
                    self.sat.add_clause([sentence])

    def accuse(
        self,
        accuser: Character,
        suspect: Character,
        weapon: Weapon,
        room: Room,
        is_correct: bool,
    ):
        if is_correct:
            return

    def matrix(self) -> List[List[Optional[bool]]]:
        """
        game state in matrix form
        """

        matrix = []

        for card in Card.deck():
            row = []
            for place in self.places():
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
            columns=[p.name.lower() for p in self.places()],
            index=[c.name.lower() for c in Card.deck()],
        )

        def fmt(x):
            return {None: "-", True: 1, False: 0}[x]

        return df.applymap(fmt)

    def places(self):
        """
        locations where a card can be
        """

        return [Case.FILE] + self.players

    def initial_clauses(self) -> List[List[int]]:
        """
        establish base logic for the game. things that all players know
        before gameplay even starts
        """

        file = Case.FILE
        clauses = []

        """
        each card in at least one place
        """

        for card in Card.deck():
            clause = []
            for place in self.places():
                clause.append(Card.to_atomic_sentence(card, place))
            clauses.append(clause)

        """
        if card is in one place, it can't be in another place
        """

        for card in Card.deck():
            for a, b in combinations(self.places(), 2):
                clause = [
                    -Card.to_atomic_sentence(card, a),
                    -Card.to_atomic_sentence(card, b),
                ]
                clauses.append(clause)

        """
        at least one card of each category in case file
        """

        for category in {Weapon, Room, Character}:
            clause = [Card.to_atomic_sentence(i, file) for i in category]
            clauses.append(clause)

        """
        no two cards in each category are in case file
        """

        for category in {Weapon, Room, Character}:
            for a, b in combinations(category, 2):
                clause = [
                    -Card.to_atomic_sentence(a, file),
                    -Card.to_atomic_sentence(b, file),
                ]
                clauses.append(clause)

        return clauses