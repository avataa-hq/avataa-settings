from enum import Enum
from typing import Optional, Any, Dict

from pydantic import BaseModel, Field

from v1.database.models.process import FilterSet


class JoinOperators(Enum):
    AND = "AND"
    OR = "OR"


class ProcessFilterModel(BaseModel):
    column: dict
    operator: str = Field(min_length=1)
    value: str = Field(min_length=1)

    class Config:
        use_enum_values = True


class ProcessFilterSetModel(BaseModel):
    name: str = Field(min_length=1)
    filters: Any = Field(...)
    public: bool | None = Field(False)
    join_operator: Optional[JoinOperators] = Field(...)
    tmo_info: dict
    priority: int
    hidden: bool | None = Field(False)

    class Config:
        use_enum_values = True

    def to_orm(self, user: str, user_id: str):
        return FilterSet(
            name=self.name,
            filters=self.filters,
            join_operator=self.join_operator,
            created_by=user,
            created_by_sub=user_id,
            public=self.public,
            hidden=self.hidden,
        )


class ProcessFilterSetPatchModel(BaseModel):
    id: int = Field(gt=0)
    name: Optional[str] = None
    filters: Optional[Any] = None
    public: Optional[bool] = None
    join_operator: Optional[JoinOperators] = None
    tmo_info: Optional[dict] = None
    priority: Optional[int] = None
    hidden: Optional[bool] = None

    class Config:
        use_enum_values = True


class ProcessFilterSetModelInfoBase(BaseModel):
    id: int


class TmoInfo(BaseModel):
    data: Dict[str, Any] = {}


class ProcessFilterSetModelInfo(
    ProcessFilterSetModel, ProcessFilterSetModelInfoBase
):
    pass


class ProcessFilterSetModelInfoWithOwner(ProcessFilterSetModelInfo):
    owner: bool
    tmo_info: TmoInfo
    priority: int
