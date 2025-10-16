from operator import or_

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.database import Database
from v1.database import ObjectParamsTable
from v1.routers.object_params.models import (
    ExistingTableConfig,
    TableConfigInfo,
    TableObjectParams,
)
from v1.routers.object_params.util import change_default_value
from v1.security.security_data_models import UserData
from v1.security.security_factory import security

"""
Endpoints for working with possible object params on the web.
"""

router = APIRouter(prefix="/object/params", tags=["object:params"])


@router.get("/default", response_model=ExistingTableConfig)
async def get_default_object_params(
    tmo_id: int = Query(default=...),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = (
        select(ObjectParamsTable)
        .where(
            ObjectParamsTable.tmo_id == tmo_id,
            ObjectParamsTable.default == true(),
            or_(
                ObjectParamsTable.public == true(),
                ObjectParamsTable.created_by_sub == user_data.id,
            ),
        )
        .order_by(ObjectParamsTable.public)
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if rows is None:
        raise HTTPException(status_code=404, detail="Default value not set yet")
    row = rows[0]
    return row.__dict__


@router.get("/", response_model=list[TableConfigInfo])
async def get_all_object_settings(
    tmo_id: int = Query(default=...),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = (
        select(ObjectParamsTable)
        .where(
            ObjectParamsTable.tmo_id == tmo_id,
            or_(
                ObjectParamsTable.public == true(),
                ObjectParamsTable.created_by_sub == user_data.id,
            ),
        )
        .order_by(ObjectParamsTable.id)
    )
    settings = await session.execute(query)
    settings = settings.scalars().fetchall()
    if len(settings) == 0:
        raise HTTPException(status_code=404, detail="Settings not found")
    return [s.__dict__ for s in settings]


@router.get("/{setting_id}", response_model=ExistingTableConfig)
async def get_object_settings(
    setting_id: int = Path(...),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    query = select(ObjectParamsTable).where(
        ObjectParamsTable.id == setting_id,
        or_(
            ObjectParamsTable.public == true(),
            ObjectParamsTable.created_by_sub == user_data.id,
        ),
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if not rows:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting = rows[0]
    return setting.__dict__


@router.post("/", status_code=201, response_model=int)
async def create_object_settings(
    tmo_id: int = Query(default=...),
    setting: TableObjectParams = Body(...),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    if setting.default:
        await change_default_value(
            session=session,
            tmo_id=tmo_id,
            user_id=user_data.id,
            public=setting.public,
            forced_default=forced_default,
        )
    try:
        setting_orm = setting.to_orm(
            user=user_data.name, user_id=user_data.id, tmo_id=tmo_id
        )
        session.add(setting_orm)
        await session.commit()
    except IntegrityError as e:
        print(e)
        raise HTTPException(
            status_code=409, detail=f"Name [{setting.name}] already exists"
        )
    await session.refresh(setting_orm)
    return setting_orm.id


@router.put("/{setting_id}", status_code=204)
async def update_object_settings(
    setting_id: int = Path(...),
    update_item: TableObjectParams = Body(...),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Updates the settings with the specified name.
    Returns an error if the settings name already exists or id does not exist
    """
    query = select(ObjectParamsTable).where(
        ObjectParamsTable.id == setting_id,
        or_(
            ObjectParamsTable.public == true(),
            ObjectParamsTable.created_by_sub == user_data.id,
        ),
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if not rows:
        raise HTTPException(status_code=404, detail="Setting not found")
    item: ObjectParamsTable = rows[0]

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
            tmo_id=item.tmo_id,
            user_id=user_data.id,
            public=update_item.public,
            forced_default=forced_default,
        )

    item.update_from(update_item.dict())
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as e:
        print(e)
        raise HTTPException(
            status_code=409, detail=f"Name [{update_item.name}] already exists"
        )


@router.delete("/{setting_id}", status_code=204)
async def delete_object_settings(
    setting_id: int = Path(...),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Deletes the setting by its identifier, if the setting does not exist, it raises an error
    """
    # deleting setting
    query = select(ObjectParamsTable).where(
        ObjectParamsTable.id == setting_id,
        or_(
            ObjectParamsTable.public == true(),
            ObjectParamsTable.created_by_sub == user_data.id,
        ),
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if not rows:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting_orm = rows[0]

    if setting_orm.public and setting_orm.default and not forced_default:
        raise HTTPException(
            status_code=409,
            detail="The value is used as default. To remove, use the forced option",
        )

    await session.delete(setting_orm)
    await session.commit()
