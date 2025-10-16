from sqlalchemy import String, JSON, PrimaryKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..model import Base


class UserSettingsOrm(Base):
    __tablename__ = "user_settings"

    user: Mapped[str] = mapped_column("username", String, nullable=False)
    key: Mapped[str] = mapped_column("key", String, nullable=False)
    settings: Mapped[dict] = mapped_column("settings", JSON, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("username", "key", name="user_settings_pkey"),
        Index("user_settings_key_username_index", "username", "key"),
    )
