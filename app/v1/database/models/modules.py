""" "DB models for Modules"""

import datetime

from sqlalchemy import Column, String, ForeignKey, JSON, BigInteger, text
from sqlalchemy.orm import Mapped, mapped_column
from ..model import Base


class Module(Base):
    __tablename__ = "modules"

    name: str = Column("name", String, primary_key=True)
    custom_name: str = Column("custom_name", String, unique=True)

    def update_from(self, item: dict):
        for key, value in item.items():
            if key not in self.__dict__:
                continue
            setattr(self, key, value)


class ModuleSettings(Base):
    __tablename__ = "module_settings"

    module_name: Mapped[str] = mapped_column(
        "module",
        String,
        ForeignKey("modules.name", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    settings: Mapped[dict] = mapped_column("settings", JSON, nullable=False)


class ModuleSettingsLogs(Base):
    __tablename__ = "module_settings_logs"

    id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=False, primary_key=True
    )
    domain: Mapped[str] = mapped_column(
        String, ForeignKey("modules.name", ondelete="CASCADE"), nullable=False
    )
    variable: Mapped[str]
    user: Mapped[str] = mapped_column(nullable=False)
    change_time: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"), index=True
    )
    old_value: Mapped[str | None]
    new_value: Mapped[str | None]
