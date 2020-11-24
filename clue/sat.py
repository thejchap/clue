from typing import List, Tuple, Optional, Set, Union, Dict
from dataclasses import dataclass, field
from pysat.solvers import Maplesat as Solver
from pandas import DataFrame
from clue import card, util


def matrix(players: List[card.Character], cnf: List[List[int]]) -> Dict:
    """
    iterate over game knowledge, output matrix of
    conclusions. for each bit of knowledge,
    if its solvable with an assumption, ensure it can't
    be disproven by the inverse of the assumption
    """

    matrix = {}
    sat = Solver(bootstrap_with=cnf)

    def test(crd: card.Card, place: card.Card) -> Optional[bool]:
        literal = util.encode_literal(crd, place)
        a = sat.solve(assumptions=[literal])

        if not a:
            return a

        b = sat.solve(assumptions=[-literal])

        if not b:
            return a

        return None

    for c in card.Card.deck():
        row = {}
        for place in [card.Case.FILE, *players]:
            row[place.value] = test(c, place)
        matrix[c.value] = row

    return matrix


def notepad(players: List[card.Character], cnf: List[List[int]]) -> DataFrame:
    """
    pretty print our understanding of game state
    """

    df = DataFrame.from_dict(matrix(players, cnf), orient="index")
    df.columns = df.columns.map(lambda c: card.Card.find(c).name.lower())

    def fmt(x):
        return {None: "-", True: 1, False: 0}[x]

    return df.applymap(fmt)


def dpll(cnf: List[Set[int]], assignments: Set[int] = set()) -> Tuple[bool, Set[int]]:
    """
    simple implementation of dpll algorithm. gonna use the other implementation that was
    written by a bunch of PHDs and won some awards for now
    """

    if not cnf:
        return True, assignments

    if any(not c for c in cnf):
        return False, set()

    l = abs(next(next(l for l in c) for c in cnf))
    new = [c for c in cnf if l not in c]
    new = [c.difference({-l}) for c in new]
    r, a = dpll(new, (assignments - {-l}) | {l})
    if r:
        return r, a

    new = [c for c in cnf if -l not in c]
    new = [c.difference({l}) for c in new]
    r, a = dpll(new, (assignments - {l}) | {-l})
    if r:
        return r, a

    return False, set()
