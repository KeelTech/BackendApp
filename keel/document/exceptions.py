
class DocumentInvalid(Exception):

    """This exception will be raised if document is invalid"""

    def __init__(self, message, *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)
