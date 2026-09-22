from collections import deque


class SessionMemory:
    """
    Stores recent conversation messages in memory.

    This memory exists only while the application
    is running.
    """

    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages

        self.messages = deque(
            maxlen=max_messages
        )


    def add_message(
        self,
        role: str,
        content: str,
    ):
        """
        Add a new conversation message.
        """

        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )


    def get_messages(self) -> list[dict]:
        """
        Return all messages currently stored
        in session memory.
        """

        return list(
            self.messages
        )


    def clear(self):
        """
        Remove all session messages.
        """

        self.messages.clear()


    def size(self) -> int:
        """
        Return number of stored messages.
        """

        return len(
            self.messages
        )