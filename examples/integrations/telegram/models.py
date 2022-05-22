import datetime

from pydantic import BaseModel

from typing import Dict, List, Union, Any

# https://github.com/python/typing/issues/182 - That's how Guido does it.
JSONType = Union[
    Dict[str, Any],
    List[Any],
]


class ScrapedData(BaseModel):
    resource: int
    data:  JSONType
    created: datetime.datetime
    modified: datetime.datetime
