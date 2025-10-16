from pydantic import BaseModel, Field, validator  # noqa

from v1.database import ColorRangeTable


class ColorRangeInList(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    public: bool = Field(...)
    default: bool = Field(...)
    created_by: str = Field(...)


class ColorRangeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    layer: str = Field(..., min_length=1)
    attribute: str = Field(..., min_length=1)
    range: dict = Field(...)
    public: bool | None = Field(False)
    default: bool | None = Field(False)

    @validator("range")
    def range_chk(cls, v):
        if len(v) == 0:
            raise ValueError("value must contain at least one element")
        return v

    def to_orm(self, user: str, user_id: str):
        return ColorRangeTable(
            name=self.name,
            layer=self.layer,
            attribute=self.attribute,
            range=self.range,
            created_by=user,
            created_by_sub=user_id,
            public=self.public,
            default=self.default,
        )


class ColorRangeUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    range: dict = Field(...)
    public: bool = Field(...)
    default: bool = Field(...)

    @validator("range")
    def range_chk(cls, v):
        if len(v) == 0:
            raise ValueError("value must contain at least one element")
        return v


class ColorRangeResponse(BaseModel):
    name: str = Field(..., min_length=1)
    range: dict = Field(...)
    public: bool = Field(...)
    default: bool = Field(...)
    created_by: str = Field(...)


class ExistingTableConfig(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    range: dict = Field(...)
    public: bool = Field(...)
    default: bool = Field(...)
    created_by: str = Field(...)
