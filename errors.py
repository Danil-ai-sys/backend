Name: Sobar Danil 
Group: PO 25-Z 
Date: 28.09.26

class MessageNotFound(Exception):
    """Raised by the storage layer when a message does not exist."""

    def __init__(self, message_id: int) -> None:
        self.message_id = message_id
        super().__init__(f"Message {message_id} was not found")


class ChatFull(Exception):
    """Raised by the storage layer when the configured message limit is reached."""

    def __init__(self, max_messages: int) -> None:
        self.max_messages = max_messages
        super().__init__(f"Chat reached its limit of {max_messages} messages")
