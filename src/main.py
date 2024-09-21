from fastapi import FastAPI
from src.logic.lobby import list_lobbies

app = FastAPI()

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola, FastAPI!"}

@app.get("home/get-lobbies")
def get_lobbies():
    games =  list_lobbies()
    return {games}