from typing import Literal

from pydantic import BaseModel


class Fleet(BaseModel):
    name: str
    size: Literal['xs', 's', 'm', 'l', 'xl', '2xl', '3xl']
    count: int = 1
    region: Literal['us-east', 'us-west']
