

class MapGlossError(Exception):

    def __init__(self, message):
        self.message = message


class MissingDatasetError(MapGlossError):
    pass


class TrainTestUnspecifiedError(MapGlossError):
    pass

class VariablePathError(MapGlossError):
    pass