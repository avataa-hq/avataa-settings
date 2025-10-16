from typing import Annotated, Literal

from pydantic import BaseModel, Field, AfterValidator, ConfigDict


def check_range_length(value: dict):
    if len(value) == 0:
        raise ValueError("value must contain at least one element")
    return value


class ColorRangeBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    direction: Literal["asc", "desc"] = "asc"

    tmo_id: str = Field(..., alias="tmoId", min_length=1)
    tprm_id: str = Field(..., alias="tprmId", min_length=1)
    val_type: str = Field("float", alias="valType", min_length=1)
    name: str = Field(..., min_length=1)
    public: bool | None = Field(False)
    default: bool | None = Field(False)


class ColorRangeCreate(ColorRangeBase):
    with_indeterminate: bool | None = Field(None, alias="withIndeterminate")
    with_cleared: bool | None = Field(None, alias="withCleared")
    value_type: Literal["General", "Percent", "Hex", "Line"] = Field(...)
    ranges: Annotated[dict, AfterValidator(check_range_length)] = Field(...)


class ColorRangeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    val_type: str | None = Field(None, alias="valType", min_length=1)
    value_type: Literal["General", "Percent", "Hex", "Line"] | None = Field(
        None
    )
    with_indeterminate: bool | None = Field(None, alias="withIndeterminate")
    with_cleared: bool | None = Field(None, alias="withCleared")
    direction: Literal["asc", "desc"] = "asc"
    ranges: Annotated[dict, AfterValidator(check_range_length)] | None = Field(
        None
    )
    public: bool | None = Field(None)
    default: bool | None = Field(None)


class ColorRangeResponse(ColorRangeCreate):
    id_: int = Field(..., alias="id")
    created_by: str = Field(...)
    created_by_sub: str = Field(...)


class ColorRangeDescriptionResponse(ColorRangeBase):
    id_: int = Field(..., alias="id")
    created_by: str = Field(...)
    created_by_sub: str = Field(...)
