Name: Sobar Danil 
Group: PO 25-Z 
Date: 28.09.26

import json
import logging
from dataclasses import asdict
from pathlib import Path

from config import settings
from errors import ChatFull, MessageNotFound
from models import Message

logger = logging.getLogger(__name__)

DATA_FILE = Path(__file__).parent / "messages.json"

_messages: dict[int, Message] = {}
_next_id: int = 1


def load() -> None:
    global _messages, _next_id

    if not DATA_FILE.exists():
        _messages = {}
        _next_id = 1
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    _messages = {item["id"]: Message(**item) for item in raw}
    _next_id = max(_messages, default=0) + 1


def save() -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            [asdict(m) for m in _messages.values()],
            f,
            ensure_ascii=False,
            indent=2,
        )


def list_all(room_id: int | None = None) -> list[Message]:
    values = list(_messages.values())
    if room_id is not None:
        values = [m for m in values if m.room_id == room_id]
    return values


def get(message_id: int) -> Message:
    message = _messages.get(message_id)
    if message is None:
        raise MessageNotFound(message_id)
    return message


def create(room_id: int, author_id: int, text: str) -> Message:
    global _next_id

    if len(_messages) >= settings.max_messages:
        raise ChatFull(settings.max_messages)

    message = Message(id=_next_id, room_id=room_id, author_id=author_id, text=text)
    _messages[message.id] = message
    _next_id += 1
    save()
    logger.info("Created message id=%s in room_id=%s", message.id, room_id)

    if len(_messages) * 10 >= settings.max_messages * 9:
        logger.warning(
            "Chat is at %s/%s messages (90%% or more full)",
            len(_messages),
            settings.max_messages,
        )
    return message


def put(message_id: int, text: str, pinned: bool = False) -> Message:
    message = get(message_id)
    message.text = text
    message.pinned = pinned
    save()
    return message


def patch(
    message_id: int, text: str | None = None, pinned: bool | None = None
) -> Message:
    message = get(message_id)
    if text is not None:
        message.text = text
    if pinned is not None:
        message.pinned = pinned
    save()
    return message


def delete(message_id: int) -> None:
    del _messages[get(message_id).id]
    save()
    logger.info("Deleted message id=%s", message_id)
