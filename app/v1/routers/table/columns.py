from operator import or_

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.database import Database
from v1.database import ColumnsTable
from v1.routers.table.models import (
    TableColumns,
    ExistingTableConfigColumnsEmpty,
    TableConfigColumnsInfo,
    ExistingTableConfigColumns,
)
from v1.routers.table.util import change_default_value
from v1.security.security_data_models import UserData
from v1.security.security_factory import security

"""
Endpoints for working with view columns on the web
"""

router = APIRouter(prefix="/table/columns", tags=["table:columns"])


@router.get(
    "/default/tmo/{tmo_id}",
    response_model=ExistingTableConfigColumnsEmpty,
    response_model_exclude_unset=True,
)
async def get_default_columns(
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
    tmo_id: int = Path(..., gt=0),
):
    """
    Returns the default for columns
    """
    query = (
        select(ColumnsTable)
        .where(
            ColumnsTable.tmo_id == tmo_id,
            ColumnsTable.default == true(),
            or_(
                ColumnsTable.public == true(),
                ColumnsTable.created_by_sub == user_data.id,
            ),
        )
        .order_by(ColumnsTable.public)
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if rows is None:
        response = dict()
    else:
        row = rows[0]
        response = row.__dict__
    return response


@router.get("/tmo/all", response_model=list[TableConfigColumnsInfo])
async def get_all_table_columns_for_all_tmo(
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Returns all saved settings for displaying columns on the frontend for all tmo.
    Data returns sorted by id
    """
    query = (
        select(ColumnsTable)
        .where(ColumnsTable.created_by_sub == user_data.id)
        .order_by(ColumnsTable.id)
    )
    user_columns = await session.execute(query)
    user_columns = user_columns.scalars().fetchall()
    user_columns_tmo_ids = [x.tmo_id for x in user_columns]

    query = (
        select(ColumnsTable)
        .where(
            ColumnsTable.tmo_id.notin_(user_columns_tmo_ids),
            ColumnsTable.public == true(),
        )
        .order_by(ColumnsTable.id)
    )
    columns = await session.execute(query)
    columns = columns.scalars().fetchall()
    res = user_columns + columns
    if len(res) == 0:
        return []
    return [s.__dict__ for s in res]


@router.get("/tmo/{tmo_id}", response_model=list[TableConfigColumnsInfo])
async def get_all_table_columns(
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
    tmo_id: int = Path(..., gt=0),
):
    """
    Returns all saved settings for displaying columns on the frontend. Data returns sorted by id
    """
    query = (
        select(ColumnsTable)
        .where(
            ColumnsTable.tmo_id == tmo_id,
            or_(
                ColumnsTable.public == true(),
                ColumnsTable.created_by_sub == user_data.id,
            ),
        )
        .order_by(ColumnsTable.id)
    )
    settings = await session.execute(query)
    settings = settings.scalars().fetchall()
    if len(settings) == 0:
        return []
    return [s.__dict__ for s in settings]


@router.get("/setting/{setting_id}", response_model=ExistingTableConfigColumns)
async def get_table_columns(
    setting_id: int = Path(...),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Returns one setting corresponding to its id. If the setting does not exist, it raises an error
    """
    query = select(ColumnsTable).where(
        ColumnsTable.id == setting_id,
        or_(
            ColumnsTable.public == true(),
            ColumnsTable.created_by_sub == user_data.id,
        ),
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if not rows:
        raise HTTPException(status_code=404, detail="Setting not found")
    setting = rows[0]
    return setting.__dict__


@router.post("/tmo/{tmo_id}", status_code=201, response_model=int)
async def create_table_columns(
    setting: TableColumns = Body(...),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
    tmo_id: int = Path(...),
):
    """
    Saves settings with the specified name.
    In response, it gives the identifier of the saved settings.
    Returns an error if the settings name already exists
    """
    if setting.default:
        await change_default_value(
            session=session,
            table=ColumnsTable,
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


@router.put("/setting/{setting_id}", status_code=204)
async def update_table_columns(
    setting_id: int = Path(...),
    update_item: TableColumns = Body(...),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Updates the settings with the specified name.
    Returns an error if the settings name already exists or id does not exist
    """
    query = select(ColumnsTable).where(
        ColumnsTable.id == setting_id,
        or_(
            ColumnsTable.public == true(),
            ColumnsTable.created_by_sub == user_data.id,
        ),
    )
    response = await session.execute(query)
    rows = response.fetchone()
    if not rows:
        raise HTTPException(status_code=404, detail="Setting not found")
    item: ColumnsTable = rows[0]

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
            table=ColumnsTable,
            user_id=user_data.id,
            public=update_item.public,
            forced_default=forced_default,
            tmo_id=item.tmo_id,
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


@router.delete("/setting/{setting_id}", status_code=204)
async def delete_table_columns(
    setting_id: int = Path(...),
    forced_default: bool = Query(False),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """
    Deletes the setting by its identifier, if the setting does not exist, it raises an error
    """
    # deleting setting
    query = select(ColumnsTable).where(
        ColumnsTable.id == setting_id,
        or_(
            ColumnsTable.public == true(),
            ColumnsTable.created_by_sub == user_data.id,
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
