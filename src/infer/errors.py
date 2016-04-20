

class InferError(Exception):

    def __init__(self, message):
        self.message = message


class InvalidContainerTypeError(InferError):
    pass


class InvalidFileTypeError(InferError):
    pass
