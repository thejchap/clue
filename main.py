from __future__ import annotations
from typing import List, Any, Optional
from fastapi import FastAPI, status, HTTPException, Request
from pydantic import BaseModel
from clue.logic import LOGIC, matrix
from clue.card import Character
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict
from uuid import uuid4 as uuid
import json


class GameService:
    def __init__(self):
        self.db: Dict[str, Any] = {}

    def create(self, req: GameReq) -> GameRes:
        game_id = str(uuid())
        defaults = {
            "id": game_id,
            "cnf": [],
            "next_seq": 0,
            "events": [],
            "matrix": matrix([Character(c) for c in req.players]),
        }
        game = {**defaults, **req.dict()}
        self.db[game_id] = game
        self.event(game_id, "init", {"players": [Character(c) for c in req.players]})
        return GameRes(**self.db[game_id])

    def index(self) -> List[GameRes]:
        return [GameRes(**g) for g in self.db.values()]

    def show(self, id: str) -> GameRes:
        attrs = self.db.get(id)

        if not attrs:
            raise HTTPException(status_code=404)

        return GameRes(**attrs)

    def event(self, id: str, name: str, args: Dict) -> GameRes:
        if name not in LOGIC:
            raise HTTPException(status_code=422)

        attrs = self.db.get(id)

        if not attrs:
            raise HTTPException(status_code=404)

        game = GameRes(**attrs)
        seq = game.next_seq
        game.next_seq += 1
        cnf = LOGIC[name](**args)
        game_cnf = game.cnf + cnf
        attrs = {
            "id": str(uuid()),
            "name": name,
            "cnf": cnf,
            "game_cnf": game_cnf,
            "seq": seq,
        }
        event = EventRes(**attrs)
        game.events.append(event)
        game.cnf = game_cnf
        self.db[id] = game.dict()
        return GameRes(**game.dict())


class EventRes(BaseModel):
    id: str
    seq: int
    name: str
    cnf: List[List[int]]
    game_cnf: List[List[int]]


class GameReq(BaseModel):
    me: int
    players: List[int]


class GameRes(BaseModel):
    id: str
    me: int
    players: List[int]
    next_seq: int
    cnf: List[List[int]]
    events: List[EventRes]
    matrix: List[List[Optional[bool]]]


app = FastAPI()
service = GameService()


@app.post("/games", response_model=GameRes, status_code=status.HTTP_201_CREATED)
def games_create(req: GameReq):
    return service.create(req)


@app.get("/games", response_model=List[GameRes])
def games_index():
    return service.index()


@app.get("/games/{id}", response_model=GameRes)
def games_show(id: str):
    return service.show(id)


@app.post("/games/{id}/{event_name}", response_model=GameRes)
async def game_event(id: str, event_name: str, req: Request):
    return service.event(id, event_name, json.loads(await req.body()))
