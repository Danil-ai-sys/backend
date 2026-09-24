Name: Sobar Danil 
Group: PO 25-Z 
Date: 24.09.26

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import storage
from models import Room, User

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "kilc-chat")

users: dict[int, User] = {}
rooms: dict[int, Room] = {}


def seed() -> None:
    alice = User(id=1, name="Alice")
    bob = User(id=2, name="Bob")
    users[alice.id] = alice
    users[bob.id] = bob

    room = Room(id=1, name="Python study group")
    room.add_member(alice.id)
    room.add_member(bob.id)
    rooms[room.id] = room


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()
    storage.load()  # <- load() runs at startup
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)


class MessageCreate(BaseModel):
    room_id: int
    author_id: int
    text: str


class MessagePut(BaseModel):
    text: str
    pinned: bool = False


class MessagePatch(BaseModel):
    text: str | None = None
    pinned: bool | None = None


@app.get("/messages")
def list_messages(room_id: int | None = None):
    return storage.list_all(room_id)


@app.get("/messages/{message_id}")
def get_message(message_id: int):
    message = storage.get(message_id)
    if message is None:
        raise HTTPException(404, "message not found")
    return message


@app.post("/messages", status_code=201)
def create_message(body: MessageCreate):
    if body.room_id not in rooms:
        raise HTTPException(404, "room not found")
    if body.author_id not in users:
        raise HTTPException(404, "author not found")
    message = storage.create(body.room_id, body.author_id, body.text)
    rooms[body.room_id].last_message_id = message.id
    return message


@app.put("/messages/{message_id}")
def replace_message(message_id: int, body: MessagePut):
    message = storage.put(message_id, body.text, body.pinned)
    if message is None:
        raise HTTPException(404, "message not found")
    return message


@app.patch("/messages/{message_id}")
def update_message(message_id: int, body: MessagePatch):
    message = storage.patch(message_id, body.text, body.pinned)
    if message is None:
        raise HTTPException(404, "message not found")
    return message


@app.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: int):
    if not storage.delete(message_id):
        raise HTTPException(404, "message not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
