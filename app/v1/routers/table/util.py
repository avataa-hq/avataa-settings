from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, true, false


async def get_default_value(
    session: AsyncSession, table, user_id: str, public: bool, tmo_id: int
):
    query = select(table).filter(
        table.default == true(), table.public == public, table.tmo_id == tmo_id
    )
    if not public:
        query = query.filter(table.created_by_sub == user_id)
    response = await session.execute(query)
    response = response.scalar()
    return response


async def change_default_value(
    session: AsyncSession,
    table,
    user_id: str,
    public: bool,
    forced_default: bool,
    tmo_id: int,
):
    default_item = await get_default_value(
        session=session,
        table=table,
        user_id=user_id,
        public=public,
        tmo_id=tmo_id,
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
