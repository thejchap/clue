API=clue.api:api

install:
	@pip install -r requirements.txt

server:
	@uvicorn ${API}

server.dev:
	@uvicorn ${API} --reload