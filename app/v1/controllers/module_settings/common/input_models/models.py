from pydantic import BaseModel, Field


class ModelSettingsCreteModel(BaseModel):
    module_name: str = Field()
    settings: dict = Field()


class ModelSettingsUpdateModel(BaseModel):
    module_name: str = Field()
    settings: dict = Field()
