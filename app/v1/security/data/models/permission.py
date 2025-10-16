from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class Permission:
    id: Mapped[int] = mapped_column(primary_key=True)
    permission: Mapped[str] = mapped_column(String, nullable=False)
    create: Mapped[bool] = mapped_column(Boolean, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, nullable=False)
    update: Mapped[bool] = mapped_column(Boolean, nullable=False)
    delete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    admin: Mapped[bool] = mapped_column(Boolean, nullable=False)
