from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class MSLOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    change_time: datetime
    user: str
    domain: str
    variable: str
    old_value: str | None = None
    new_value: str | None = None


class MSLPaginationMeta(BaseModel):
    total_count: int
    page_count: int


class MSLPaginationOutput(BaseModel):
    meta: MSLPaginationMeta
    elements: List[MSLOutput]
