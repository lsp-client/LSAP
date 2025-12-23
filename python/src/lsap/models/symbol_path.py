from pydantic import BaseModel

from lsap.models.base import LocateText


class SymbolPathRequest(BaseModel):
    locate: LocateText
