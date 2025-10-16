from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.models.modules import Module


async def get_modules_by_names(
    module_names: List[str], session: AsyncSession
) -> Sequence[Module]:
    """Returns List of Module instance."""

    stmt = select(Module).where(Module.name.in_(module_names))
    res = await session.execute(stmt)
    return res.scalars().all()
