from __future__ import annotations

import datetime

from sqlalchemy import DateTime, String, CheckConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID as _UUIDC, JSONB
from uuid import UUID, uuid4

from ..model import Base

UUIDC = _UUIDC(as_uuid=True)


class State(Base):
    __tablename__ = "state"

    id: Mapped[UUID] = mapped_column(
        UUIDC, default=uuid4, primary_key=True, index=True, nullable=False
    )
    value: Mapped[dict] = mapped_column(
        JSONB(none_as_null=True), nullable=False
    )
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.datetime.now, nullable=False
    )
    expire_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    created_by: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("expire_date >= creation_date", name="exp_qe_cr"),
    )
