import json


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

    def get(self) -> str:
        return json.dumps(self.__dict__)

    def dict2obj(dict):
        return json.loads(json.dumps(dict), object_hook=NodeToTracker)
