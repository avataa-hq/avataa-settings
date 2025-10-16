from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, model_validator, field_validator


class MSLSortDirections(str, Enum):
    ASC = "asc"
    DESC = "desc"


class MSLSortBy(str, Enum):
    DOMAIN = "domain"
    VARIABLE = "variable"
    USER = "user"
    CHANGE_TIME = "change_time"
    OLD_VALUE = "old_value"
    NEW_VALUE = "new_value"


class MSLSortInput(BaseModel):
    sort_by: MSLSortBy
    sort_direction: MSLSortDirections


class MSLFilterInput(BaseModel):
    module_names: List[str] = None
    fields_keys: List[str] = None
    from_date: datetime = None
    users: List[str] = None
    new_value: str | None = None
    old_value: str | None = None
    to_date: datetime = None
    sort_by: List[MSLSortInput] = None
    limit: int = Field(default=20, gt=0)
    offset: int = Field(default=0, ge=0)

    @field_validator("from_date", "to_date", mode="after")
    def convert_into_dt_without_time_zone(cls, v):
        if v:
            return v.replace(tzinfo=None)

    @model_validator(mode="after")
    def check_dates(self):
        from_date = self.from_date
        to_date = self.to_date

        if from_date is not None and to_date is not None:
            if from_date >= to_date:
                raise ValueError(
                    "the from_date cannot be greater than or equal to_date"
                )
        return self
