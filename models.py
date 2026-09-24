Name: Sobar Danil 
Group: PO 25-Z 
Date: 24.09.26

from dataclasses import dataclass, field


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
