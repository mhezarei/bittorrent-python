from project.messages.message import Message


class SizeInformation(Message):
    def __init__(self, src_name: str, dest_name: str, filename: str,
                 size: int):
        """
        examples:
            size of the file:
                {src_name, dest_name, filename, size of the file}
        """

        # add assertions

        super().__init__()
        self.src_name = src_name
        self.dest_name = dest_name
        self.filename = filename
        self.size = size
