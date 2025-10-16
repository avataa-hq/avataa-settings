"""Utils for Module router"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.models.modules import Module


async def check_source_exists(session: AsyncSession, module_name: str):
    """Raises error if Module with name={module_name} does not exist, otherwise return Module instance"""
    stmt = select(Module).where(Module.name == module_name)
    res = await session.execute(stmt)
    res = res.scalars().first()
    if res is None:
        raise HTTPException(
            status_code=404,
            detail=f"Source with name={module_name} does not exist!",
        )
    return res
