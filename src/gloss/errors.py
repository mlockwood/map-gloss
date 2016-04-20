

class GlossError(Exception):

    def __init__(self, message):
        self.message = message


class MissingDatasetError(GlossError):
    pass


class VariablePathError(GlossError):
    pass


class InvalidClassifierError(GlossError):
    pass


class ClassifierWeightError(GlossError):
    pass


class InvalidClassifierWeightError(GlossError):
    pass


class InvalidContainerTypeError(GlossError):
    pass


class MissingGlossGoldStandardError(GlossError):
    pass