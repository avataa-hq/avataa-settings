from pydantic import BaseModel, Field, JsonValue


class UserSettingsBase(BaseModel):
    settings: JsonValue = Field(default_factory=lambda: dict())


class UserSettingsCreate(UserSettingsBase):
    pass


class UserSettingsUpdate(UserSettingsBase):
    pass


class UserSettingsResponse(UserSettingsBase):
    pass
