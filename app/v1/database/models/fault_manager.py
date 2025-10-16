from sqlalchemy import String, Boolean, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..model import Base


class FaultColorRangeTable(Base):
    __tablename__ = "fm_color"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    range: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_by_sub: Mapped[str] = mapped_column(String, nullable=False)
    public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __tableargs__ = UniqueConstraint(name)

    def update_from(self, item: dict):
        for key, value in item.items():
            if key not in self.__dict__:
                continue
            setattr(self, key, value)


class FaultColumnsTable(Base):
    __tablename__ = "fm_columns"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String)
    value: Mapped[dict] = mapped_column(JSONB)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_by_sub: Mapped[str] = mapped_column(String, nullable=False)
    public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __tableargs__ = UniqueConstraint(tmo_id, name, created_by_sub)

    def update_from(self, item: dict):
        for key, value in item.items():
            if key not in self.__dict__:
                continue
            setattr(self, key, value)


class FaultFiltersTable(Base):
    __tablename__ = "fm_filters"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmo_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True)
    value: Mapped[dict] = mapped_column(JSONB)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_by_sub: Mapped[str] = mapped_column(String, nullable=False)
    public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    __tableargs__ = UniqueConstraint(
        tmo_id, name, created_by_sub, public, default
    )

    def update_from(self, item: dict):
        for key, value in item.items():
            if key not in self.__dict__:
                continue
            setattr(self, key, value)
