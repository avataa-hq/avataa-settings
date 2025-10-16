from sqlalchemy import String, Boolean, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..model import Base

"""
Color criteria for displaying hexbins on the map
"""


class ColorRangeTable(Base):
    __tablename__ = "map"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    layer: Mapped[str] = mapped_column(String, nullable=False)
    attribute: Mapped[str] = mapped_column(String, nullable=False)
    range: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_by_sub: Mapped[str] = mapped_column(String, nullable=False)
    public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __tableargs__ = UniqueConstraint(name, layer, attribute, created_by)

    def update_from(self, item: dict):
        for key, value in item.items():
            if key not in self.__dict__:
                continue
            setattr(self, key, value)


class ColorRangeTableNew(Base):
    __tablename__ = "color_range"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmo_id: Mapped[str] = mapped_column(String, nullable=False)
    tprm_id: Mapped[str] = mapped_column(String, nullable=False)
    val_type: Mapped[str] = mapped_column(
        String, nullable=False, server_default="float"
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    value_type: Mapped[str] = mapped_column(String, nullable=False)
    with_indeterminate: Mapped[bool] = mapped_column(Boolean, nullable=True)
    with_cleared: Mapped[bool] = mapped_column(Boolean, nullable=True)
    ranges: Mapped[dict] = mapped_column(JSON, nullable=False)
    public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    direction: Mapped[str] = mapped_column(
        String, default="asc", nullable=False
    )
    default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_by_sub: Mapped[str] = mapped_column(String, nullable=False)

    __tableargs__ = UniqueConstraint(
        tmo_id, tprm_id, name, created_by, name="color_range_unique"
    )

    def update_from(self, item: dict):
        for key, value in item.items():
            if key not in self.__dict__:
                continue
            setattr(self, key, value)
