from pydantic import BaseModel, Field, validator  # noqa


class ModuleCreate(BaseModel):
    name: str = Field(...)
    custom_name: str = Field(...)
