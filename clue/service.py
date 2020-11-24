from __future__ import annotations
from typing import List, Any, Optional, Set, Tuple
from os import getenv
from inspect import getfullargspec
import json
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict
from uuid import uuid4 as uuid
from pydantic import BaseModel
from fastapi import HTTPException
from redis import from_url
from clue import game, card, util, sat


class EventRecord(BaseModel):
    id: str
    seq: int
    name: str
    args: Dict
    cnf: List[List[int]]
    game_cnf: List[List[int]]
    matrix: Dict


class EventRes(BaseModel):
    id: str
    seq: int
    name: str
    args: Dict
    matrix: Dict


class EventReq(BaseModel):
    pass


class HandReq(EventReq):
    cards: Set[int]
    me: int
    players: List[int]


class SuggestionReq(EventReq):
    suggester: int
    suspect: int
    weapon: int
    room: int
    refuter: Optional[int]
    card_shown: Optional[int]


class AccusationReq(EventReq):
    accuser: int
    suspect: int
    weapon: int
    room: int
    is_correct: bool


class GameRecord(BaseModel):
    id: str
    me: Optional[int]
    players: List[int]
    next_seq: int
    cnf: List[List[int]]
    events: List[EventRecord]
    matrix: Dict


class GameRes(BaseModel):
    id: str
    me: Optional[int]
    players: List[int]
    events: List[EventRes]
    matrix: Dict


Cnf = List[List[int]]
EventResult = Tuple[GameRecord, Cnf]


def _event(func):
    @wraps(func)
    def wrapper(self, id: str, req: EventReq):
        game = self.show(id)
        seq = game.next_seq
        game.next_seq += 1
        game, cnf = func(self, game, req)
        game_cnf = game.cnf + cnf
        game.cnf = game_cnf
        players = [card.Character(p) for p in game.players]
        matrix = sat.matrix(players, game_cnf)
        attrs = {
            "id": str(uuid()),
            "name": func.__name__,
            "args": req.dict(),
            "cnf": cnf,
            "game_cnf": game_cnf,
            "seq": seq,
            "matrix": matrix,
        }
        event = EventRecord(**attrs)
        game.events.append(event)
        game.matrix = matrix
        self.db.set(f"game:{id}", game.json())
        return GameRecord(**game.dict())

    return wrapper


class GameService:
    def __init__(self):
        self.db = from_url(getenv("REDIS_URL", "redis://localhost:6379"))

    def create(self) -> GameRecord:
        game_id = str(uuid())
        state = {
            "id": game_id,
            "cnf": [],
            "next_seq": 0,
            "events": [],
            "matrix": {},
            "players": [],
            "me": None,
        }
        self.db.set(f"game:{game_id}", json.dumps(state))
        self.db.sadd("games", f"game:{game_id}")
        refreshed = json.loads(self.db.get(f"game:{game_id}"))
        return GameRecord(**refreshed)

    def index(self) -> List[GameRecord]:
        ids = self.db.smembers("games")
        games = [json.loads(g) for g in self.db.mget(ids)]
        return [GameRecord(**g) for g in games]

    def show(self, id: str) -> GameRecord:
        attrs = self.db.get(f"game:{id}")

        if not attrs:
            raise HTTPException(status_code=404)

        return GameRecord(**json.loads(attrs))

    @_event
    def hand(self, state: GameRecord, req: HandReq) -> EventResult:
        players = [card.Character(p) for p in req.players]
        cards = {card.Card.find(c) for c in req.cards}
        me = card.Character(req.me)

        state.me = req.me
        state.players = req.players

        return state, game.hand(me, cards, players)

    @_event
    def accuse(self, state: GameRecord, req: AccusationReq) -> EventResult:
        players = [card.Character(p) for p in state.players]
        accuser = card.Character(req.accuser)
        suspect = card.Character(req.suspect)
        weapon = card.Weapon(req.weapon)
        room = card.Room(req.room)

        return state, game.accuse(
            players, accuser, suspect, weapon, room, req.is_correct
        )

    @_event
    def suggest(self, state: GameRecord, req: SuggestionReq) -> EventResult:
        players = [card.Character(p) for p in state.players]
        suggester = card.Character(req.suggester)
        suspect = card.Character(req.suspect)
        weapon = card.Weapon(req.weapon)
        room = card.Room(req.room)
        refuter = card.Character(req.refuter) if req.refuter else None
        card_shown = card.Card.find(req.card_shown) if req.card_shown else None

        return state, game.suggest(
            players, suggester, suspect, weapon, room, refuter, card_shown
        )