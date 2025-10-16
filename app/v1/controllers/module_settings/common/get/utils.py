from typing import List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.models.modules import ModuleSettings


async def get_modules_settings_by_names(
    module_names: List[str], session: AsyncSession
) -> Sequence[ModuleSettings]:
    """Returns List of Module instance."""

    stmt = select(ModuleSettings).where(
        ModuleSettings.module_name.in_(module_names)
    )
    res = await session.execute(stmt)
    return res.scalars().all()
