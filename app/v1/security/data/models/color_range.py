from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from v1.database.model import Base
from v1.security.data.models.permission import Permission


class ColorRangeTablePermission(Base, Permission):
    __tablename__ = "permission_map"

    parent_id: Mapped[int] = mapped_column(
        ForeignKey("map.id", ondelete="CASCADE", onupdate="CASCADE")
    )
