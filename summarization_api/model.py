from abc import ABCMeta, abstractmethod
from enum import Enum


class ApiExceptionName(Enum):
    MISSING_REQUIRED_PARAMETER = "missing-required-parameter"
    ID_NOT_FOUND = "id-not-found"
    TEXT_TOO_SHORT = "text-too-short"


class TextIdNotFoundError(Exception):
    pass


class TooManyTextsDbError(Exception):
    pass


class SummarizationApiException(Exception):
    def __init__(self, code: int, name: ApiExceptionName, description: str):
        self.code: int = code
        self.name: ApiExceptionName = name
        self.description: str = description

    def build_message(self) -> dict:
        return {
            "code": self.code,
            "name": self.name.value,
            "description": self.description,
        }


class AbstractTextHandler(metaclass=ABCMeta):
    @abstractmethod
    def get_text_from_id(self, text_id: str) -> str:
        """Return the text with the corresponding text_id

        Parameters
        ----------
        text_id
            text identifier

        Returns
        -------
            the text corresponding to text_id
        """

    @abstractmethod
    def store_text_and_get_id(self, text: str) -> str:
        """Stores text and return id

        Parameters
        ----------
        text
            str text to store and identify

        Returns
        -------
            text id

        """
