from typing import Tuple, List, Optional
from pandas import DataFrame
from pysat.solvers import Maplesat as Solver
from .card import Card, Character, Case


def encode_literal(card: Card, place: Card) -> int:
    """
    smallest unit of propositional logic
    card is in a place. encode in 8 bit int
    """

    return card.value << 3 | place.value


def decode_literal(atom: int) -> Tuple[Card, Card]:
    """
    take atom and return card values
    """

    return Card.find(atom >> 3), Card.find(atom & 7)


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
