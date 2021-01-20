from typing import Tuple
from project.messages.message import Message


class FileCommunication(Message):
    def __init__(self, src_name: str, dest_name: str, filename: str,
                 indices: Tuple[int, int], idx=-1, data: bytes = None):
        """
        example:
            range of the desired file:
            "data" contains the actual bytes of the data and it is None
            when a node tells another node that it needs the specified
            range of the file.
            idx means which part of the total files am I? -1 for the first.
            maximum number of bytes held in data is 64KB.
            {src_name, dest_name, filename, [0, 100,000), idx, [bytes of data]}
        """
        
        # add assertions
        
        super().__init__()
        self.src_name = src_name
        self.dest_name = dest_name
        self.filename = filename
        self.range = indices
        self.idx = idx
        self.data = data
