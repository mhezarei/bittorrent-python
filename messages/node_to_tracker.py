from messages.message import Message


class NodeToTracker(Message):
    def __init__(self, name: str, mode: str, filename: str):
        """
        examples:
            {name, "need", filename}
            {name, "have", filename}
            {name, "exit", ""}
        """
        # add assertions

        super().__init__()
        self.name = name
        self.mode = mode
        self.filename = filename
