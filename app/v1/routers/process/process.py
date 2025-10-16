from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import and_, or_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.database import Database
from v1.database.models.process import FilterSet
from v1.routers.process.models import (
    ProcessFilterSetModel,
    ProcessFilterSetModelInfo,
    ProcessFilterSetPatchModel,
)
from v1.routers.process.utils import (
    check_if_named_filter_exists,
    get_filterset_by_id,
)
from v1.security.security_data_models import UserData
from v1.security.security_factory import security

router = APIRouter(prefix="/process", tags=["Process:filters"])


@router.post(
    "/filterSet", status_code=201, response_model=ProcessFilterSetModelInfo
)
async def create_filter_set(
    filter_set: ProcessFilterSetModel,
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    await check_if_named_filter_exists(filter_set.name, user_data.id, session)

    new_filter_set = filter_set.to_orm(user_data.name, user_data.id)
    new_filter_set.tmo_info = filter_set.tmo_info
    new_filter_set.priority = filter_set.priority
    session.add(new_filter_set)
    await session.commit()
    await session.refresh(new_filter_set)

    return new_filter_set


@router.get("/filterSet", status_code=200)
async def read_all_filters_sets(
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    stmt = select(FilterSet).where(FilterSet.created_by_sub == user_data.id)
    own_true_filters = await session.execute(stmt)
    own_true_filters = own_true_filters.scalars().all()

    stmt = select(FilterSet).where(
        FilterSet.public == true(), FilterSet.created_by_sub != user_data.id
    )
    own_false_filters = await session.execute(stmt)
    own_false_filters = own_false_filters.scalars().all()

    res = []
    if own_true_filters:
        for x in own_true_filters:
            item = x.__dict__
            item.update({"owner": True})
            res.append(item)

    if own_false_filters:
        for x in own_false_filters:
            item = x.__dict__
            item.update({"owner": False})
            res.append(item)
    return res


@router.patch("/filterSet", status_code=200)
async def batch_update_filter_set(
    filters: List[ProcessFilterSetPatchModel],
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    filters_data = dict()

    check_new_filters_names_conditions = []

    for filter_item in filters:
        item_as_dict = filter_item.dict(exclude_unset=True)

        filter_set_id = item_as_dict.get("id")

        name = item_as_dict.get("name")
        if name:
            check_new_filters_names_conditions.extend(
                [
                    and_(
                        FilterSet.name == name,
                        FilterSet.created_by_sub == user_data.id,
                        FilterSet.id != filter_set_id,
                    ),
                    and_(
                        FilterSet.name == name,
                        FilterSet.public == true(),
                        FilterSet.id != filter_set_id,
                    ),
                ]
            )  # noqa

        filters_data[filter_set_id] = item_as_dict

    if check_new_filters_names_conditions:
        stmt = select(FilterSet).filter(or_())
        res = await session.execute(stmt)
        res = res.scalars().all()

        if res:
            raise HTTPException(
                status_code=400,
                detail=f"FilterSets named: {[filter_set.name for filter_set in res]} already exist.",
            )

    stmt = select(FilterSet).where(
        FilterSet.id.in_(list(filters_data)),
        FilterSet.created_by_sub == user_data.id,
    )
    res = await session.execute(stmt)
    res = res.scalars().all()

    if len(res) != len(filters_data):
        existing_ids = {item.id for item in res}
        not_existing_filter_ids = [
            item_id
            for item_id in filters_data.keys()
            if item_id not in existing_ids
        ]
        raise HTTPException(
            status_code=404,
            detail=f"FilterSets with id: {not_existing_filter_ids} do not exist!",
        )

    resp_data = list()
    for filter_item in res:
        new_data = filters_data[filter_item.id]
        for k, v in new_data.items():
            setattr(filter_item, k, v)
        session.add(filter_item)
        resp_data.append(filter_item)
    await session.commit()

    return resp_data


@router.put(
    "/filterSet/{filter_id}",
    status_code=200,
    response_model=ProcessFilterSetModelInfo,
)
async def update_filter_set(
    filter_set: ProcessFilterSetModel,
    filter_id: int = Path(),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    inst = await get_filterset_by_id(filter_id, user_data.id, session)

    stmt = select(FilterSet).filter(
        or_(
            and_(
                FilterSet.name == filter_set.name,
                FilterSet.created_by_sub == user_data.id,
                FilterSet.id != filter_id,
            ),
            and_(
                FilterSet.name == filter_set.name,
                FilterSet.public == true(),
                FilterSet.id != filter_id,
            ),  # noqa
        )
    )

    res = await session.execute(stmt)
    res = res.first()

    if res is not None:
        raise HTTPException(
            status_code=400,
            detail=f"FilterSet named {filter_set.name} already exists.",
        )

    for k, v in filter_set.dict(exclude_unset=True).items():
        setattr(inst, k, v)
    session.add(inst)
    await session.commit()
    await session.refresh(inst)
    return inst


@router.get(
    "/filterSet/{filter_id}",
    status_code=200,
    response_model=ProcessFilterSetModelInfo,
)
async def read_filter_set_by_id(
    filter_id: int = Path(),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    stmt = select(FilterSet).where(
        or_(
            and_(
                FilterSet.id == filter_id,
                FilterSet.created_by_sub == user_data.id,
            ),
            and_(FilterSet.id == filter_id, FilterSet.public == true()),
        )
    )
    res = await session.execute(stmt)
    res = res.scalars().first()

    if res is None:
        raise HTTPException(
            status_code=400,
            detail=f"FilterSet with id = {filter_id} does not exist!",
        )
    return res


@router.delete(
    "/filterSet/{filter_id}",
    status_code=204,
)
async def delete_filter_set(
    filter_id: int = Path(),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    inst = await get_filterset_by_id(filter_id, user_data.id, session)

    await session.delete(inst)
    await session.commit()
    return {"msg": "FilterSet deleted successfully"}
