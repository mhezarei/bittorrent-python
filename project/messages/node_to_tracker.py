class NodeToTracker:
    def __init__(self, name: str, mode: str, message: str):
        """
        examples:
            {name, "need", filename}
            {name, "have", filename}
            {name, "exit", ""}
        """
        # add assertions

        self.name = name
        self.mode = mode
        self.message = message

    def get(self) -> dict:
        return self.__dict__
