from operator import or_

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from asyncpg.exceptions import UniqueViolationError, NotNullViolationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, true

from v1.database.database import Database
from v1.database import ColorRangeTable
from v1.routers.map.models import (
    ColorRangeInList,
    ColorRangeCreate,
    ColorRangeUpdate,
    ColorRangeResponse,
    ExistingTableConfig,
)
from v1.routers.map.util import change_default_value
from v1.security.security_factory import security
from v1.security.security_data_models import UserData

"""
Endpoints for working with map colors on the web
"""

router = APIRouter(prefix="/map/color", tags=["map:colors"], deprecated=True)


@router.get("/default", response_model=ExistingTableConfig)
async def get_default_color_range(
    layer: str = Query(..., min_length=1),
    attribute: str = Query(..., min_length=1),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Returns the default for columns
    """
    query = (
        select(ColorRangeTable)
        .where(
            ColorRangeTable.default == true(),
            ColorRangeTable.attribute == attribute,
            ColorRangeTable.layer == layer,
            or_(
                ColorRangeTable.public == true(),
                ColorRangeTable.created_by_sub == user_data.id,
            ),
        )
        .order_by(ColorRangeTable.public)
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if rows is None:
        raise HTTPException(status_code=404, detail="Default value not set yet")
    row = rows[0]
    return row.__dict__


@router.get(
    "/attributes_with_existing_default_color_range", response_model=list[str]
)
async def get_attributes_with_existing_default_color_range(
    layer: str = Query(..., min_length=1),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Returns a list of attributes for which there is an existing default color range (public or private)
    """
    query = (
        select(ColorRangeTable.attribute)
        .where(
            ColorRangeTable.default == true(),
            ColorRangeTable.layer == layer,
            or_(
                ColorRangeTable.public == true(),
                ColorRangeTable.created_by_sub == user_data.id,
            ),
        )
        .order_by(ColorRangeTable.attribute)
        .distinct()
    )
    response = await session.execute(query)
    response = response.all()
    response = [item[0] for item in response]
    return response


@router.get("/", response_model=list[ColorRangeInList])
async def get_ranges_list(
    layer: str = Query(..., min_length=1),
    attribute: str = Query(..., min_length=1),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = select(ColorRangeTable).filter(
        ColorRangeTable.attribute == attribute,
        ColorRangeTable.layer == layer,
        or_(
            ColorRangeTable.public == true(),
            ColorRangeTable.created_by_sub == user_data.id,
        ),
    )
    response = await session.execute(query)
    response = response.scalars()
    return [r.__dict__ for r in response]


@router.get("/{id}", response_model=ColorRangeResponse)
async def get_range(
    id_: int = Path(..., alias="id"),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = select(ColorRangeTable).filter(
        ColorRangeTable.id == id_,
        or_(
            ColorRangeTable.public == true(),
            ColorRangeTable.created_by_sub == user_data.id,
        ),
    )
    response = await session.execute(query)
    response = response.scalar()
    if response is None:
        raise HTTPException(
            status_code=404, detail="Does not exist or action not allowed"
        )
    return response.__dict__


@router.post("/")
async def post_range(
    item: ColorRangeCreate,
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    if item.default:
        await change_default_value(
            session=session,
            user_id=user_data.id,
            layer=item.layer,
            attribute=item.attribute,
            public=item.public,
            forced_default=forced_default,
        )
    item = item.to_orm(user=user_data.name, user_id=user_data.id)
    session.add(item)
    try:
        await session.flush()
        await session.commit()
    except IntegrityError as e:
        print(e)
        await session.rollback()
        if isinstance(e.orig, UniqueViolationError):
            raise HTTPException(
                status_code=409,
                detail="duplicate key value violates unique constraint",
            )
        elif isinstance(e.orig, NotNullViolationError):
            raise HTTPException(status_code=409, detail="null value in column")
        else:
            raise e
    return item.id


@router.put("/{id}", status_code=204)
async def put_range(
    id_: int = Path(..., alias="id"),
    update_item: ColorRangeUpdate = Body(..., alias="item"),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    jwt_info: UserData = Depends(security),
):
    query = select(ColorRangeTable).filter(
        ColorRangeTable.id == id_,
        or_(
            ColorRangeTable.public == true(),
            ColorRangeTable.created_by_sub == jwt_info.id,
        ),
    )
    response = await session.execute(query)
    item = response.fetchone()
    if item is None:
        raise HTTPException(
            status_code=404, detail="Does not exist or action not allowed"
        )
    item = item[0]

    become_not_default = item.default and not update_item.default
    if become_not_default and not forced_default:
        raise HTTPException(
            status_code=409,
            detail="Used as the default value. "
            "First assign a new default value or use the force attribute",
        )

    become_default = not item.default and update_item.default
    become_public = update_item.default and (
        update_item.public and not item.public
    )

    if become_default or become_public:
        await change_default_value(
            session=session,
            user_id=jwt_info.id,
            layer=item.layer,
            attribute=item.attribute,
            public=update_item.public,
            forced_default=forced_default,
        )
    item.update_from(update_item.dict())
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as e:
        print(e)
        await session.rollback()
        if isinstance(e.orig, UniqueViolationError):
            raise HTTPException(
                status_code=409,
                detail="duplicate key value violates unique constraint",
            )
        elif isinstance(e.orig, NotNullViolationError):
            raise HTTPException(status_code=409, detail="null value in column")
        else:
            raise e


@router.delete("/{id}", status_code=204)
async def delete_map_range(
    id_: int = Path(..., alias="id"),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = select(ColorRangeTable).filter(
        ColorRangeTable.id == id_,
        ColorRangeTable.created_by_sub == user_data.id,
    )
    response = await session.execute(query)
    item = response.fetchone()
    if item is None:
        raise HTTPException(
            status_code=404, detail="Does not exist or action not allowed"
        )
    item = item[0]

    if item.public and item.default and not forced_default:
        raise HTTPException(
            status_code=409,
            detail="The value is used as default. To remove, use the forced option",
        )

    await session.delete(item)
    await session.commit()
