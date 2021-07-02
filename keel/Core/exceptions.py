
class InvalidDataType(Exception):

    """This exception will be raised if Data is invalid"""

    def __init__(self, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
