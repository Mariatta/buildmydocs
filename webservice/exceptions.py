import http


class BuildMyDocsException(Exception):
    """Base exception."""


class HTTPException(BuildMyDocsException):

    """A general exception to represent HTTP responses."""

    def __init__(self, status_code: http.HTTPStatus, *args):
        self.status_code = status_code
        if args:
            super().__init__(*args)
        else:
            super().__init__(status_code.phrase)


class BadRequest(HTTPException):
    """The request is invalid.

    Used for 4XX HTTP errors.
    """


class ReadthedocsBroken(HTTPException):

    """Exception for 5XX HTTP responses."""
