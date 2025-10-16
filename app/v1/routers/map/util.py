from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, true, false

from v1.database import ColorRangeTable


async def get_default_value(
    session: AsyncSession,
    user_id: str,
    layer: str,
    attribute: str,
    public: bool,
):
    query = select(ColorRangeTable).filter(
        ColorRangeTable.default == true(),
        ColorRangeTable.public == public,
        ColorRangeTable.layer == layer,
        ColorRangeTable.attribute == attribute,
    )
    if not public:
        query = query.filter(ColorRangeTable.created_by_sub == user_id)
    response = await session.execute(query)
    response = response.scalar()
    return response


async def change_default_value(
    session: AsyncSession,
    user_id: str,
    layer: str,
    attribute: str,
    public: bool,
    forced_default: bool,
):
    default_item: ColorRangeTable | None = await get_default_value(
        session=session,
        user_id=user_id,
        layer=layer,
        attribute=attribute,
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
