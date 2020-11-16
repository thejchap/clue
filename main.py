from __future__ import annotations
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from clue.card import Character
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict
from uuid import uuid4 as uuid


@dataclass
class Database:
    games: Dict[int, Game] = field(default_factory=dict)
    events: Dict[int, Event] = field(default_factory=dict)


class Game(BaseModel):
    me: int
    players: List[int]
    next_seq: int = 0
    cnf: List[List[int]]


class Event(BaseModel):
    seq: int
    name: str
    cnf: List[List[int]]
    game_cnf: List[List[int]]
    game_id: int


app = FastAPI()
db = Database()


@app.post("/games")
def games_create(game: Game):
    db.games[id(game)] = game
    return game


@app.get("/games")
def games_index():
    return list(db.games.values())


@app.post("/events")
def events_create():
    return {"id": 1}