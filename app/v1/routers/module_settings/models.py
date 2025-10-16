from pydantic import BaseModel, Field


class ModelSettingsInfo(BaseModel):
    module_name: str = Field()
    settings: dict = Field()
