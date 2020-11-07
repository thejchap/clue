from __future__ import annotations
from typing import List, Tuple, Optional, Set, Union
from enum import Enum


class Card(Enum):
    @staticmethod
    def find(i: int) -> Card:
        """
        lookup card by int value
        """

        if i < 1:
            return Case(i)
        if i <= 6:
            return Character(i)
        if i <= 12:
            return Weapon(i)
        if i <= 22:
            return Room(i)
        raise ValueError(i)

    @staticmethod
    def places():
        yield Case.FILE
        for char in Character:
            yield char

    @staticmethod
    def deck():
        for char in Character:
            yield char
        for weapon in Weapon:
            yield weapon
        for room in Room:
            yield room

    @staticmethod
    def to_atomic_sentence(card: Card, place: Card) -> int:
        """
        smallest unit of propositional logic
        card is in a place. encode in 8 bit int
        """

        return card.value << 3 | place.value

    @staticmethod
    def from_atomic_sentence(atom: int) -> Tuple[Card, Card]:
        """
        take atom and return card values
        """

        return Card.find(atom >> 3), Card.find(atom & 7)


class Case(Card):
    FILE = 0


class Character(Card):
    SCARLETT = 1
    GREEN = 2
    MUSTARD = 3
    PLUM = 4
    PEACOCK = 5
    WHITE = 6


class Weapon(Card):
    CANDLESTICK = 7
    DAGGER = 8
    PIPE = 9
    REVOLVER = 10
    ROPE = 11
    WRENCH = 12


class Room(Card):
    KITCHEN = 13
    BALLROOM = 14
    CONSERVATORY = 15
    DINING_ROOM = 16
    CELLAR = 17
    BILLIARD_ROOM = 18
    LIBRARY = 19
    LOUNGE = 20
    HALL = 21
    STUDY = 22