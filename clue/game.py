from __future__ import annotations
from typing import List, Tuple, Optional, Set, Union
from enum import Enum
from uuid import uuid4 as uuid
from itertools import combinations, cycle
from dataclasses import dataclass, field
from pandas import DataFrame
from pysat.solvers import Maplesat as Solver
from .card import Card, Character, Room, Weapon, Case
from .util import encode_literal


@dataclass
class Game:
    me: Character
    players: List[Character]

    def __post_init__(self):
        """
        initialization. set up our solver with stuff that all players
        take for granted
        """

        self.player_set = set(self.players)

        if self.me not in self.player_set:
            raise ValueError(self.me)

        self.init()

    def hand(self, cards: Set[Card]):
        """
        add knowledge of my hand
        """

        clauses = []

        for card in Card.deck():
            atom = encode_literal(card, self.me)
            atom = atom if card in cards else -atom
            clauses.append([atom])

        print(clauses)

    def test(self, card: Card, place: Card) -> Optional[bool]:
        """
        if its solvable with this assumption, ensure it can't
        be disproven by the inverse of the assumption
        """

        sat = Solver(bootstrap_with=[])
        literal = encode_literal(card, place)
        a = sat.solve(assumptions=[literal])

        if not a:
            return a

        b = sat.solve(assumptions=[-literal])

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

        if suggester not in self.player_set:
            raise ValueError(suggester)

        if refuter and refuter not in self.player_set:
            raise ValueError(refuter)

        clauses = []

        if refuter:
            """
            somebody showed one of the 3 cards
            """

            if card_shown:
                """
                i was the suggester so i got to see the card
                """

                sentence = encode_literal(card_shown, refuter)
                clauses.append([sentence])
            else:
                """
                refuter has one of the 3 cards
                """

                clause = []
                for card in [suspect, weapon, room]:
                    sentence = encode_literal(card, refuter)
                    clause.append(sentence)
                clauses.append(clause)

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
                        sentence = -encode_literal(card, player)
                        clauses.append([sentence])
        else:
            """
            we learned that nobody has any of these cards.
            i might, if i was bluffing or whateve
            """

            for player in self.players:
                if player == suggester:
                    continue

                for card in [suspect, weapon, room]:
                    sentence = -encode_literal(card, player)
                    clauses.append([sentence])

        print(clauses)

    def accuse(
        self,
        accuser: Character,
        suspect: Character,
        weapon: Weapon,
        room: Room,
        is_correct: bool,
    ):
        """
        TODO
        """

        if accuser not in self.player_set:
            raise ValueError(accuser)

        if is_correct:
            raise Exception("WINNER")
        raise Exception("LOSER")

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

    def init(self):
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
                clause.append(encode_literal(card, place))
            clauses.append(clause)

        """
        if card is in one place, it can't be in another place
        """

        for card in Card.deck():
            for a, b in combinations(self.places(), 2):
                clause = [
                    -encode_literal(card, a),
                    -encode_literal(card, b),
                ]
                clauses.append(clause)

        """
        at least one card of each category in case file
        """

        for category in {Weapon, Room, Character}:
            clause = [encode_literal(i, file) for i in category]
            clauses.append(clause)

        """
        no two cards in each category are in case file
        """

        for category in {Weapon, Room, Character}:
            for a, b in combinations(category, 2):
                clause = [
                    -encode_literal(a, file),
                    -encode_literal(b, file),
                ]
                clauses.append(clause)

        print(clauses)