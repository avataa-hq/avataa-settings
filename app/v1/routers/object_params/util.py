from fastapi import HTTPException
from sqlalchemy import select, true, false
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database import ObjectParamsTable


async def get_default_value(
    session: AsyncSession, tmo_id: int, user_id: str, public: bool
):
    query = select(ObjectParamsTable).filter(
        ObjectParamsTable.default == true(),
        ObjectParamsTable.public == public,
        ObjectParamsTable.tmo_id == tmo_id,
    )
    if not public:
        query = query.filter(ObjectParamsTable.created_by_sub == user_id)
    response = await session.execute(query)
    response = response.scalar()
    return response


async def change_default_value(
    session: AsyncSession,
    tmo_id: int,
    user_id: str,
    public: bool,
    forced_default: bool,
):
    default_item = await get_default_value(
        session=session, tmo_id=tmo_id, user_id=user_id, public=public
    )
    if default_item is not None:
        if not forced_default:
            raise HTTPException(
                status_code=409,
                detail="The default value already exists. "
                "You must apply forced replacement if this change is necessary",
            )
        else:
            default_item.default = false()
            session.add(default_item)
