from typing import List, Tuple, Optional, Set, Union
from dataclasses import dataclass, field


Disjunctive = Set[int]
Cnf = List[Disjunctive]


@dataclass
class Solver:
    knowledge: Cnf = field(default_factory=list)

    def add_clause(self, disjunctive: Disjunctive):
        """
        add disjunctive to our knowledge base (conjunctive)
        """

        self.knowledge.append(disjunctive)

    def test(self, literal: int) -> Optional[bool]:
        a, _ = dpll(self.knowledge + [{literal}])

        if not a:
            return a

        b, _ = dpll(self.knowledge + [{-literal}])

        if not b:
            return a

        return None


def dpll(cnf: Cnf, assignments: Set[int] = set()) -> Tuple[bool, Set[int]]:
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
