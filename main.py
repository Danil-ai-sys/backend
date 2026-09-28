Name: Sobar Danil 
Group: PO 25-Z 
Date: 28.09.26

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import storage
from errors import ChatFull, MessageNotFound
from models import Room, User

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

APP_NAME = os.getenv("APP_NAME", "kilc-chat")

users: dict[int, User] = {}
rooms: dict[int, Room] = {}


def seed() -> None:
    users.clear()
    rooms.clear()

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
    storage.load()
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)


@app.exception_handler(MessageNotFound)
def message_not_found_handler(
    _request: Request, exc: MessageNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"code": "message_not_found", "detail": str(exc)},
    )


@app.exception_handler(ChatFull)
def chat_full_handler(_request: Request, exc: ChatFull) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"code": "chat_full", "detail": str(exc)},
    )


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
    try:
        return storage.get(message_id)
    except MessageNotFound:
        logger.info("Message lookup failed: id=%s", message_id)
        raise


@app.post("/messages", status_code=201)
def create_message(body: MessageCreate):
    if body.room_id not in rooms:
        raise HTTPException(404, "room not found")
    if body.author_id not in users:
        raise HTTPException(404, "author not found")

    try:
        message = storage.create(body.room_id, body.author_id, body.text)
    except ChatFull:
        logger.warning("Message creation rejected because the chat is full")
        raise

    rooms[body.room_id].last_message_id = message.id
    return message


@app.put("/messages/{message_id}")
def replace_message(message_id: int, body: MessagePut):
    try:
        return storage.put(message_id, body.text, body.pinned)
    except MessageNotFound:
        logger.info("Message replacement failed: id=%s", message_id)
        raise


@app.patch("/messages/{message_id}")
def update_message(message_id: int, body: MessagePatch):
    try:
        return storage.patch(message_id, body.text, body.pinned)
    except MessageNotFound:
        logger.info("Message update failed: id=%s", message_id)
        raise


@app.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: int):
    try:
        storage.delete(message_id)
    except MessageNotFound:
        logger.info("Message deletion failed: id=%s", message_id)
        raise


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
