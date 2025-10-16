from abc import ABCMeta, abstractmethod

from pydantic import BaseModel, Field  # noqa

from v1.database import ColumnsTable, FiltersTable

"""
This stores the generic data models that are used to receive or return typed responses in endpoints.
"""


class TableConfigInfo(BaseModel):
    id: int = Field(...)
    tmo_id: int = Field(...)
    name: str = Field(...)
    public: bool = Field(...)
    default: bool = Field(...)
    created_by: str = Field(...)


class ExistingTableConfigEmpty(BaseModel):
    id: int | None = None
    tmo_id: int | None = None
    name: str | None = None
    value: dict | None = None
    public: bool | None = None
    default: bool | None = None
    created_by: str | None = None


class ExistingTableConfig(BaseModel):
    id: int = Field(...)
    tmo_id: int = Field(...)
    name: str = Field(...)
    value: dict | None = Field(None)
    public: bool = Field(...)
    default: bool = Field(...)
    created_by: str = Field(...)


class TableConfigBase(BaseModel):
    __metaclass__ = ABCMeta

    name: str = Field(...)
    value: dict | None = Field(None)
    public: bool = Field(...)
    default: bool = Field(...)

    @abstractmethod
    def to_orm(self, user: str, user_id: str, tmo_id: int):
        pass


class TableColumnsBase(BaseModel):
    order: list | None = Field(None)
    pinned: dict | None = Field(None)


class TableColumns(TableColumnsBase, TableConfigBase):
    def to_orm(self, user: str, user_id: str, tmo_id: int):
        return ColumnsTable(
            **self.dict(),
            created_by=user,
            created_by_sub=user_id,
            tmo_id=tmo_id,
        )


class TableConfigColumnsInfo(TableColumnsBase, TableConfigInfo):
    pass


class ExistingTableConfigColumnsEmpty(
    TableColumnsBase, ExistingTableConfigEmpty
):
    pass


class ExistingTableConfigColumns(TableColumnsBase, ExistingTableConfig):
    pass


class TableFilters(TableConfigBase):
    def to_orm(self, user: str, user_id: str, tmo_id: int):
        return FiltersTable(
            **self.dict(),
            created_by=user,
            created_by_sub=user_id,
            tmo_id=tmo_id,
        )
