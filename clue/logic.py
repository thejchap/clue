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


def hand(me: Character, cards: Set[Card]) -> List[List[int]]:
    """
    add knowledge of my hand
    """

    clauses = []

    for card in Card.deck():
        atom = encode_literal(card, me)
        atom = atom if card in cards else -atom
        clauses.append([atom])

    return clauses


def test(card: Card, place: Card) -> Optional[bool]:
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
    players: List[Character],
    suggester: Character,
    suspect: Character,
    weapon: Weapon,
    room: Room,
    refuter: Optional[Character] = None,
    card_shown: Optional[Card] = None,
) -> List[List[int]]:
    """
    a players turn. record who suggested what murder, and who, if anyone,
    refuted it. if it was our turn and we were shown a card, we can take
    that into account too
    """

    player_set = set(players)

    if suggester not in set(player_set):
        raise ValueError(suggester)

    if refuter and refuter not in set(player_set):
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

        for player in cycle(players):
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

        for player in players:
            if player == suggester:
                continue

            for card in [suspect, weapon, room]:
                sentence = -encode_literal(card, player)
                clauses.append([sentence])

    return clauses


def accuse(
    players: List[Character],
    accuser: Character,
    suspect: Character,
    weapon: Weapon,
    room: Room,
    is_correct: bool,
):
    """
    TODO
    """

    if accuser not in set(players):
        raise ValueError(accuser)

    if is_correct:
        raise Exception("WINNER")
    raise Exception("LOSER")


def matrix(players: List[Character]) -> List[List[Optional[bool]]]:
    """
    game state in matrix form
    """

    matrix = []

    for card in Card.deck():
        row = []
        for place in [Case.FILE, *players]:
            result = test(card, place)
            row.append(result)
        matrix.append(row)

    return matrix


def notepad(players: List[Character]) -> DataFrame:
    """
    pretty print our understanding of game state
    """

    df = DataFrame.from_records(
        matrix(players),
        columns=[p.name.lower() for p in [Case.FILE, *players]],
        index=[c.name.lower() for c in Card.deck()],
    )

    def fmt(x):
        return {None: "-", True: 1, False: 0}[x]

    return df.applymap(fmt)


def init(players: List[Character]):
    """
    establish base logic for the game. things that all players know
    before gameplay even starts
    """

    file = Case.FILE
    places = [file, *players]
    clauses = []

    """
    each card in at least one place
    """

    for card in Card.deck():
        clause = []
        for place in places:
            clause.append(encode_literal(card, place))
        clauses.append(clause)

    """
    if card is in one place, it can't be in another place
    """

    for card in Card.deck():
        for a, b in combinations(places, 2):
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

    return clauses


LOGIC = {
    "hand": hand,
    "suggest": suggest,
    "accuse": accuse,
    "init": init,
}
