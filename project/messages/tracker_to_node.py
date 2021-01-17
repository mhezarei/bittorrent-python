class TrackerToNode:
    def __init__(self, dest_name: str, owners: list, filename: str):
        """
        examples:
            {nameA, [B, C, D], filename}
        """
        # add assertions

        self.dest_name = dest_name
        self.owners = owners
        self.filename = filename

    def get(self) -> dict:
        return self.__dict__
