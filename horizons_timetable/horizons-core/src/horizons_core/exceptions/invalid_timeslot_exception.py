class InvalidTimeslotException(Exception):
    """Exception levée lorsqu'un créneau horaire est invalide."""

    def __init__(self, message: str):
        super().__init__(message)