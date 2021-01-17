from typing import Tuple
from project.messages.message import Message


class FileCommunication(Message):
    def __init__(self, src_name: str, dest_name: str, filename: str,
                 indices: Tuple[int, int], data: list = None):
        """
        examples:
            range of the desired file:
                "data" contains the actual bytes of the data and it isis None
                when a node tells another node that it needs the specified
                range of the file.
                {src_name, dest_name, filename, [0, 1500), [bytes of data]}
        """

        # add assertions

        super().__init__()
        self.src_name = src_name
        self.dest_name = dest_name
        self.filename = filename
        self.range = indices
        self.data = data
