class VariableError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ConditionError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class LoopError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class StructureError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class PlacementError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message 