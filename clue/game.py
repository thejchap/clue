from __future__ import annotations
from typing import List, Tuple, Optional, Set, Union
from itertools import combinations, cycle
from .card import Card, Character, Room, Weapon, Case
from .util import encode_literal


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

    if suggester not in player_set:
        raise ValueError(suggester)

    if refuter and refuter not in player_set:
        raise ValueError(refuter)

    if card_shown and card_shown not in {suspect, weapon, room}:
        raise ValueError(card_shown)

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


def hand(me: Character, cards: Set[Card], players: List[Character]):
    """
    establish base logic for the game. things that all players know
    before gameplay even starts. also add my hand
    """

    file = Case.FILE
    places = [file, *players]
    clauses = []
    player_set = set(players)

    if me not in player_set:
        raise ValueError(me)

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

    for card in Card.deck():
        atom = encode_literal(card, me)
        atom = atom if card in cards else -atom
        clauses.append([atom])

    return clauses