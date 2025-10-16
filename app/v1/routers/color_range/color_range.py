from operator import or_

from asyncpg import UniqueViolationError, NotNullViolationError
from fastapi import APIRouter, Query, Depends, HTTPException, Path, Body
from sqlalchemy import true, select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.database import Database
from v1.database.models.color_range import ColorRangeTableNew
from v1.routers.color_range.models import (
    ColorRangeCreate,
    ColorRangeUpdate,
    ColorRangeResponse,
    ColorRangeDescriptionResponse,
)
from v1.routers.color_range.utils import change_default_value
from v1.security.security_data_models import UserData
from v1.security.security_factory import security

router = APIRouter(prefix="/color_range", tags=["color"])


@router.post("/")
async def create_color_range(
    item: ColorRangeCreate,
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    orm_item = ColorRangeTableNew(
        created_by=user_data.name,
        created_by_sub=user_data.id,
        **item.model_dump(by_alias=False),
    )
    if item.default:
        await change_default_value(
            session=session,
            user_id=user_data.id,
            tmo_id=item.tmo_id,
            tprm_id=item.tprm_id,
            public=item.public,
            forced_default=forced_default,
            val_type=item.val_type,
        )
    session.add(orm_item)
    try:
        await session.flush()
        await session.commit()
    except IntegrityError as e:
        print(e)
        await session.rollback()
        if isinstance(e.orig.__cause__, UniqueViolationError):
            raise HTTPException(
                status_code=409,
                detail="duplicate key value violates unique constraint",
            )
        elif isinstance(e.orig.__cause__, NotNullViolationError):
            raise HTTPException(status_code=409, detail="null value in column")
        else:
            raise e
    return orm_item.id


@router.patch("/{id}", status_code=204)
async def update_color_range(
    id_: int = Path(..., alias="id"),
    update_item: ColorRangeUpdate = Body(..., alias="item"),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = select(ColorRangeTableNew).filter(
        ColorRangeTableNew.id == id_,
        or_(
            ColorRangeTableNew.public == true(),
            ColorRangeTableNew.created_by_sub == user_data.id,
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

    become_default = (
        (not item.default and update_item.default)
        if update_item.default is not None
        else False
    )
    become_public = (
        (update_item.default and (update_item.public and not item.public))
        if update_item.public is not None
        else False
    )

    if become_default or become_public:
        await change_default_value(
            session=session,
            user_id=user_data.id,
            tmo_id=item.tmo_id,
            tprm_id=item.tprm_id,
            public=update_item.public
            if update_item.public is not None
            else item.public,
            forced_default=forced_default,
            val_type=item.val_type,
        )

    item.update_from(
        update_item.model_dump(exclude_unset=True, exclude_none=True)
    )
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as e:
        print(e)
        await session.rollback()
        if isinstance(e.orig.__cause__, UniqueViolationError):
            raise HTTPException(
                status_code=409,
                detail="duplicate key value violates unique constraint",
            )
        elif isinstance(e.orig.__cause__, NotNullViolationError):
            raise HTTPException(status_code=409, detail="null value in column")
        else:
            raise e


@router.delete("/{id}", status_code=204)
async def delete_range(
    id_: int = Path(..., alias="id"),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = select(ColorRangeTableNew).filter(
        ColorRangeTableNew.id == id_,
        or_(
            ColorRangeTableNew.created_by_sub == user_data.id,
            ColorRangeTableNew.public == true(),
        ),
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


@router.post(
    "/filter",
    response_model=list[ColorRangeResponse | ColorRangeDescriptionResponse],
)
async def find_ranges(
    ids: list[int] | None = None,
    tmo_ids: list[str] | None = None,
    tprm_ids: list[str] | None = None,
    val_types: list[str] | None = None,
    is_default: bool | None = Body(None),
    limit: int = Body(10, qt=0, le=1000),
    offset: int = Body(0, qe=0),
    only_description: bool = Body(True),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = (
        select(ColorRangeTableNew)
        .filter(
            or_(
                ColorRangeTableNew.public == true(),
                ColorRangeTableNew.created_by_sub == user_data.id,
            )
        )
        .limit(limit)
        .offset(offset)
        .order_by(ColorRangeTableNew.id)
    )

    if ids:
        query = query.filter(ColorRangeTableNew.id.in_(ids))
    if tmo_ids:
        query = query.filter(ColorRangeTableNew.tmo_id.in_(tmo_ids))
    if tprm_ids:
        query = query.filter(ColorRangeTableNew.tprm_id.in_(tprm_ids))
    if is_default is not None:
        query = query.filter(ColorRangeTableNew.default == is_default)
    if val_types is not None:
        query = query.filter(ColorRangeTableNew.val_type.in_(val_types))
    response = await session.execute(query)
    result = [r.__dict__ for r in response.scalars().all()]
    if only_description:
        for r in result:
            del r["ranges"]
            del r["value_type"]
    return result


@router.get("/defaults", response_model=list[ColorRangeResponse])
async def get_defaults(
    tmo_id: str | None = Query(None, min_length=1),
    tprm_id: str | None = Query(None, min_length=1),
    val_type: str | None = Query(None, min_length=1),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    if not any((tmo_id, tprm_id)):
        raise HTTPException(
            status_code=422,
            detail="You must specify at least one search parameter",
        )
    query = select(
        ColorRangeTableNew,
        func.rank()
        .over(
            partition_by=ColorRangeTableNew.tprm_id,
            order_by=(
                ColorRangeTableNew.public.asc(),
                ColorRangeTableNew.id.desc(),
            ),
        )
        .label("rank"),
    ).filter(
        or_(
            ColorRangeTableNew.public == true(),
            ColorRangeTableNew.created_by_sub == user_data.id,
        ),
        ColorRangeTableNew.default == true(),
    )
    if tmo_id:
        query = query.filter(ColorRangeTableNew.tmo_id == tmo_id)
    if tprm_id:
        query = query.filter(ColorRangeTableNew.tprm_id == tprm_id)
    if val_type:
        query = query.filter(ColorRangeTableNew.val_type == val_type)
    subquery = query.subquery()
    query = select(subquery).filter(subquery.c.rank == 1)
    response = await session.execute(query)
    result = response.mappings().all()
    return result
