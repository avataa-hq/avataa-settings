from pydantic import BaseModel


class ModelSettingsOutput(BaseModel):
    module_name: str
    settings: dict
