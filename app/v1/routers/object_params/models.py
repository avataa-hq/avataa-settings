from pydantic import BaseModel, Field  # noqa

from v1.database import ObjectParamsTable

"""
This stores the generic data models that are used to receive or return typed responses in endpoints.
"""


class TableConfigInfo(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    public: bool = Field(...)
    default: bool = Field(...)
    created_by: str = Field(...)


class ExistingTableConfig(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    value: dict = Field(...)
    public: bool = Field(...)
    default: bool = Field(...)
    created_by: str = Field(...)


class TableObjectParams(BaseModel):
    name: str = Field(...)
    value: dict | None = Field(None)
    public: bool = Field(...)
    default: bool = Field(...)

    def to_orm(self, user: str, user_id: str, tmo_id):
        return ObjectParamsTable(
            **self.dict(),
            created_by=user,
            created_by_sub=user_id,
            tmo_id=tmo_id,
        )
