from abc import ABC
from loguru import logger

class IUtility(ABC):

    def __init__(self, urn: str = None, api_name: str = None) -> None:
        self.urn = urn
        
        self.api_name = api_name
        self.logger = logger.bind(urn=self.urn, api_name=self.api_name)