import json


class TrackerToNode:
    def __init__(self, dest_name: str, owners: list, filename: str):
        """
        examples:
            {nameA, [portB, portC, portD], filename}
        """
        # add assertions

        self.dest_name = dest_name
        self.owners = owners
        self.filename = filename

    def get(self) -> str:
        return json.dumps(self.__dict__)
