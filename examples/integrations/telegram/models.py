import datetime

from pydantic import BaseModel as PydanticBaseModel

from typing import Dict, List, Union, Any, Optional

# https://github.com/python/typing/issues/182 - That's how Guido does it.
JSONType = Union[
    Dict[str, Any],
    List[Any],
]


class BaseModel(PydanticBaseModel):
    id: int


class CreatedModifiedModel(BaseModel):
    created: datetime.datetime
    modified: datetime.datetime


class ActivatedDeactivatedModel(BaseModel):
    activate_date: datetime.datetime
    deactivate_date: Optional[datetime.datetime]


class TitleDescriptionModel(BaseModel):
    title: str
    description: str


class TitleDescriptionSlugModel(TitleDescriptionModel):
    slug: str


class Topic(CreatedModifiedModel, TitleDescriptionSlugModel):
    id: int


class Resource(
    CreatedModifiedModel, TitleDescriptionSlugModel, ActivatedDeactivatedModel
):
    status: int
    url: str
    priority: int
    topic: Topic


class ScrapedData(CreatedModifiedModel):
    id: int
    resource: Resource
    data: JSONType
