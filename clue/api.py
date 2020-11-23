from __future__ import annotations
from typing import List, Any, Optional, Set
import json
from functools import wraps
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict
from uuid import uuid4 as uuid
from fastapi import FastAPI, status, HTTPException, Request
from pydantic import BaseModel
from redis import Redis
from clue import game, card, util


def event(func):
    @wraps(func)
    def wrapper(self, id: str, req: EventReq):
        game = self.show(id)
        seq = game.next_seq
        game.next_seq += 1
        cnf = func(self, game, req)
        game_cnf = game.cnf + cnf
        attrs = {
            "id": str(uuid()),
            "name": func.__name__,
            "cnf": cnf,
            "game_cnf": game_cnf,
            "seq": seq,
        }
        event = EventRes(**attrs)
        game.events.append(event)
        game.cnf = game_cnf
        self.db.set(f"game:{id}", game.json())
        return GameRes(**game.dict())

    return wrapper


class GameService:
    def __init__(self):
        self.db = Redis()

    def create(self, req: GameReq) -> GameRes:
        game_id = str(uuid())
        defaults = {
            "id": game_id,
            "cnf": [],
            "next_seq": 0,
            "events": [],
            "matrix": util.matrix([card.Character(c) for c in req.players]),
        }
        state = {**defaults, **req.dict()}
        self.db.set(f"game:{game_id}", json.dumps(state))
        self.db.sadd("games", f"game:{game_id}")
        self.init(game_id, InitReq(players=req.players))
        refreshed = json.loads(self.db.get(f"game:{game_id}"))
        return GameRes(**refreshed)

    def index(self) -> List[GameRes]:
        ids = self.db.smembers("games")
        games = [json.loads(g) for g in self.db.mget(ids)]
        return [GameRes(**g) for g in games]

    def show(self, id: str) -> GameRes:
        attrs = self.db.get(f"game:{id}")

        if not attrs:
            raise HTTPException(status_code=404)

        return GameRes(**json.loads(attrs))

    @event
    def hand(self, state: GameRes, req: HandReq) -> List[List[int]]:
        cards = {card.Card.find(c) for c in req.cards}
        me = card.Character(state.me)

        return game.hand(me, cards)

    @event
    def accuse(self, state: GameRes, req: AccusationReq) -> List[List[int]]:
        players = [card.Character(p) for p in state.players]
        accuser = card.Character(req.accuser)
        suspect = card.Character(req.suspect)
        weapon = card.Weapon(req.weapon)
        room = card.Room(req.room)

        return game.accuse(players, accuser, suspect, weapon, room, req.is_correct)

    @event
    def suggest(self, state: GameRes, req: SuggestionReq) -> List[List[int]]:
        players = [card.Character(p) for p in state.players]
        suggester = card.Character(req.suggester)
        suspect = card.Character(req.suspect)
        weapon = card.Weapon(req.weapon)
        room = card.Room(req.room)
        refuter = card.Character(req.refuter) if req.refuter else None
        card_shown = card.Card.find(req.card_shown) if req.card_shown else None

        return game.suggest(
            players, suggester, suspect, weapon, room, refuter, card_shown
        )

    @event
    def init(self, state: GameRes, req: InitReq) -> List[List[int]]:
        return game.init([card.Character(p) for p in req.players])


class EventRes(BaseModel):
    id: str
    seq: int
    name: str
    cnf: List[List[int]]
    game_cnf: List[List[int]]


class GameReq(BaseModel):
    me: int
    players: List[int]


class EventReq(BaseModel):
    pass


class InitReq(EventReq):
    players: List[int]


class HandReq(EventReq):
    me: int
    cards: Set[int]


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


class GameRes(BaseModel):
    id: str
    me: int
    players: List[int]
    next_seq: int
    cnf: List[List[int]]
    events: List[EventRes]
    matrix: List[List[Optional[bool]]]


service = GameService()
api = FastAPI()


@api.post("/games", response_model=GameRes, status_code=status.HTTP_201_CREATED)
def games_create(req: GameReq):
    return service.create(req)


@api.get("/games/{id}", response_model=GameRes)
def game_show(id: str):
    return service.show(id)


@api.post("/games/{id}/hand", response_model=GameRes)
async def game_hand(id: str, req: HandReq):
    return service.hand(id, req)


@api.post("/games/{id}/suggest", response_model=GameRes)
async def game_suggest(id: str, req: SuggestionReq):
    return service.suggest(id, req)


@api.post("/games/{id}/accuse", response_model=GameRes)
async def game_accuse(id: str, req: AccusationReq):
    return service.accuse(id, req)