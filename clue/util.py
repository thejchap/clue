from typing import Tuple
from .card import Card


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
