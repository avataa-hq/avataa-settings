from fastapi import HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.models.process import FilterSet


async def check_if_named_filter_exists(
    name: str, user_id: str, session: AsyncSession
):
    """Raise error if FilterSet.name = name already exists."""
    stmt = select(FilterSet).filter(
        or_(
            and_(FilterSet.name == name, FilterSet.created_by_sub == user_id),
            and_(FilterSet.name == name, FilterSet.public == True),  # noqa
        )
    )

    res = await session.execute(stmt)
    res = res.first()

    if res is not None:
        raise HTTPException(
            status_code=400, detail=f"FilterSet named {name} already exists."
        )


async def get_filterset_by_id(
    filter_id: int, user_id: str, session: AsyncSession
):
    """Returns FilterSet instance if FilterSet with filter_id exists, otherwise raises error"""
    stmt = select(FilterSet).where(
        FilterSet.id == filter_id, FilterSet.created_by_sub == user_id
    )
    res = await session.scalar(stmt)

    if res is None:
        raise HTTPException(
            status_code=400,
            detail=f"FilterSet with id = {filter_id} does not exist!",
        )
    return res
