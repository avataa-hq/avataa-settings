from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.models.modules import Module, ModuleSettings


async def get_module_by_name_or_raise_error(
    module_name: str, session: AsyncSession
) -> Module:
    """Returns Module instance otherwise raises error."""

    stmt = select(Module).where(Module.name == module_name)
    module = await session.execute(stmt)
    module = module.scalars().first()
    if module is None:
        raise HTTPException(
            status_code=404,
            detail=f"Module named {module_name} was not founded!",
        )
    return module


async def get_module_settings_or_raise_error(
    module_name: str, session: AsyncSession
) -> ModuleSettings:
    """Returns ModuleSettings instance otherwise raises error."""
    stmt = select(ModuleSettings).where(
        ModuleSettings.module_name == module_name
    )
    settings_from_db = await session.execute(stmt)
    settings_from_db = settings_from_db.scalars().first()

    if settings_from_db is None:
        raise HTTPException(
            status_code=404,
            detail=f"Settings for module named {module_name} were not founded!",
        )

    return settings_from_db
