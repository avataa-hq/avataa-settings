from typing import List

from sqlalchemy.sql import expression

from ..model import Base
from sqlalchemy import Column, Integer, String, JSON, Boolean, UniqueConstraint


class FilterSet(Base):
    __tablename__ = "filter_set"
    id: int = Column("id", Integer, primary_key=True)
    name: str = Column("name", String, nullable=False)
    filters: List[dict] = Column("filters", JSON, nullable=False)
    join_operator: str = Column("join_operator", String, nullable=True)
    created_by: str = Column("created_by", String, nullable=False)
    created_by_sub: str = Column("created_by_sub", String, nullable=False)
    public: bool = Column("public", Boolean, nullable=False, default=False)
    tmo_info: dict = Column("tmo_info", JSON, nullable=False, default={})
    priority: int = Column("priority", Integer, nullable=False, default=1)
    hidden: bool = Column(
        "hidden",
        Boolean,
        nullable=False,
        default=False,
        server_default=expression.false(),
    )

    __tableargs__ = UniqueConstraint(
        "name", "created_by_sub", name="_user_filters"
    )
