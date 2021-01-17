from project.messages.message import Message


class TrackerToNode(Message):
    def __init__(self, dest_name: str, owners: list, filename: str):
        """
        examples:
            {nameA, [(nameB, ipB,  portB), (nameC, ipC, portC)], filename}
        """
        # add assertions

        super().__init__()
        self.dest_name = dest_name
        self.owners = owners
        self.filename = filename
