from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from v1.database.model import Base
from v1.security.data.models.permission import Permission


class ColumnsTablePermission(Base, Permission):
    __tablename__ = "permission_table_columns"

    parent_id: Mapped[int] = mapped_column(
        ForeignKey("table_columns.id", ondelete="CASCADE", onupdate="CASCADE")
    )


class FiltersTablePermission(Base, Permission):
    __tablename__ = "permission_table_filters"

    parent_id: Mapped[int] = mapped_column(
        ForeignKey("table_filters.id", ondelete="CASCADE", onupdate="CASCADE")
    )
