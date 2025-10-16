from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.models.color_range import ColorRangeTableNew


async def check_color_range_exists(
    session: AsyncSession, tmo_id: str, kpi_id: str, color_range_name: str
):
    stmt = select(ColorRangeTableNew).where(
        ColorRangeTableNew.tmo_id == tmo_id,
        ColorRangeTableNew.tprm_id == kpi_id,
        ColorRangeTableNew.name == color_range_name,
        ColorRangeTableNew.created_by == "",
    )
    kpi_exists = await session.execute(stmt)
    return kpi_exists.scalar()
