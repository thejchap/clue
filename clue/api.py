from fastapi import FastAPI, status, HTTPException, Request
from clue import service

SERVICE = service.GameService()
API = FastAPI()


@API.post("/games", response_model=service.GameRes, status_code=status.HTTP_201_CREATED)
def games_create(req: service.GameReq):
    return SERVICE.create(req)


@API.get("/games/{id}", response_model=service.GameRes)
def game_show(id: str):
    return SERVICE.show(id)


@API.post("/games/{id}/hand", response_model=service.GameRes)
async def game_hand(id: str, req: service.HandReq):
    return SERVICE.hand(id, req)


@API.post("/games/{id}/suggest", response_model=service.GameRes)
async def game_suggest(id: str, req: service.SuggestionReq):
    return SERVICE.suggest(id, req)


@API.post("/games/{id}/accuse", response_model=service.GameRes)
async def game_accuse(id: str, req: service.AccusationReq):
    return SERVICE.accuse(id, req)