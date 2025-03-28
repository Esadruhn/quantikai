class InvalidMoveError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidFileException(Exception):
    def __init__(self, message):
        super().__init__(message)
