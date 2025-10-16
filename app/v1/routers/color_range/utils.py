from fastapi import HTTPException
from sqlalchemy import false, true, select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.models.color_range import ColorRangeTableNew


async def change_default_value(
    session: AsyncSession,
    user_id: str,
    tmo_id: str,
    tprm_id: str,
    val_type: str,
    public: bool,
    forced_default: bool,
):
    default_item: ColorRangeTableNew | None = await get_default_value(
        session=session,
        user_id=user_id,
        tmo_id=tmo_id,
        tprm_id=tprm_id,
        val_type=val_type,
        public=public,
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


async def get_default_value(
    session: AsyncSession,
    user_id: str,
    tmo_id: str,
    tprm_id: str,
    val_type: str,
    public: bool,
):
    query = select(ColorRangeTableNew).filter(
        ColorRangeTableNew.default == true(),
        ColorRangeTableNew.public == public,
        ColorRangeTableNew.tmo_id == tmo_id,
        ColorRangeTableNew.tprm_id == tprm_id,
        ColorRangeTableNew.val_type == val_type,
    )
    if not public:
        query = query.filter(ColorRangeTableNew.created_by_sub == user_id)
    response = await session.execute(query)
    response = response.scalar()
    return response
