Name:Sobar Danil Group:PO 25-Z Date:22.09.26

from dataclasses import asdict, dataclass, field
import json

@dataclass
class User:
    id: int
    name: str


@dataclass
class Room:
    id: int
    name: str
    member_ids: list[int] = field(default_factory=list)
    last_message_id: int | None = None

    def add_member(self, user_id: int) -> None:
        if user_id not in self.member_ids:
            self.member_ids.append(user_id)


@dataclass
class Message:
    id: int
    room_id: int
    author_id: int
    text: str
    pinned: bool = False

    def preview(self) -> str:
        return self.text[:30]


def main() -> None:
    # Two users and one room.
    alice = User(id=1, name="Alice")
    bob = User(id=2, name="Bob")
    room = Room(id=1, name="Python study group")
    room.add_member(alice.id)
    room.add_member(bob.id)
    room.add_member(alice.id)
    messages = [
        Message(
            id=1,
            room_id=room.id,
            author_id=alice.id,
            text="Welcome to the Python study group!",
        ),
        Message(
            id=2,
            room_id=room.id,
            author_id=bob.id,
            text="Thanks! I am ready to learn dataclasses.",
            pinned=True,
        ),
        Message(
            id=3,
            room_id=room.id,
            author_id=alice.id,
            text="Our first topic is clean data models.",
        ),
    ]
    room.last_message_id = messages[-1].id
    print(room)
    print(messages[0].preview())
    print(json.dumps(asdict(messages[0]), ensure_ascii=False))
    same_message = Message(4, room.id, alice.id, "Same message")
    same_message_copy = Message(4, room.id, alice.id, "Same message")
    print(same_message == same_message_copy)

if __name__ == "__main__":
    main()
