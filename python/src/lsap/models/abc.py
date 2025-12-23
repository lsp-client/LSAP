from abc import abstractmethod

from pydantic import BaseModel


class Response(BaseModel):
    @abstractmethod
    def format(self) -> str:
        """
        Format the response to standard Markdown format for agents to consume.
        """
