API=clue.api:API

install:
	@pip install -r requirements.txt

server:
	@uvicorn ${API}

server.dev:
	@uvicorn ${API} --reload