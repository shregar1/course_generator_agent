from abstractions.error import IError


class UnexpectedResponseError(IError):

    def __init__(self, responseMessage: str, responseKey: str, http_status_code: int) -> None:

        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.http_status_code = http_status_code