from abc import ABC

from start_utils import logger

from utilities.dictionary import DictionaryUtility


class IController(ABC):

    def __init__(self, urn:str = None, api_name:str = None) -> None:
        super().__init__()
        self.urn = urn
        self.api_name = api_name
        self.logger = logger.bind(urn=self.urn)
        self.dictionary_utility = DictionaryUtility(urn=self.urn)

    async def validate_request(
        self,
        urn: str,
        request_payload: dict,
        request_headers: dict,
        api_name: str
    ):
        self.api_name = api_name
        return
