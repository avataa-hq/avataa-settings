from typing import Annotated

from asyncpg import UniqueViolationError
from fastapi import APIRouter, Depends, Body, Path, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from v1.database.database import Database
from v1.database.models.user_settings import UserSettingsOrm
from v1.routers.user_settings.models import (
    UserSettingsCreate,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from v1.security.security_data_models import UserData
from v1.security.security_factory import security

router = APIRouter(prefix="/user_settings", tags=["User Settings"])


@router.get("/")
async def get_list_of_user_settings(
    session: Annotated[
        AsyncSession, Depends(Database().get_session_with_depends)
    ],
    user_data: UserData = Depends(security),
):
    query = select(UserSettingsOrm.key).where(
        UserSettingsOrm.user == user_data.id
    )
    user_settings = await session.execute(query)
    user_settings = user_settings.scalars().all()

    return user_settings


@router.get("/{key}", response_model=UserSettingsResponse)
async def get_user_settings(
    key: Annotated[str, Path(min_length=1)],
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
) -> UserSettingsResponse:
    query = select(UserSettingsOrm).where(
        and_(UserSettingsOrm.key == key, UserSettingsOrm.user == user_data.id)
    )
    user_settings = await session.execute(query)
    user_settings = user_settings.scalar()

    if not user_settings:
        raise HTTPException(
            status_code=404, detail="Settings with given id not exist!"
        )

    return UserSettingsResponse.model_validate(
        user_settings, from_attributes=True
    )


@router.post("/{key}", response_model=UserSettingsResponse)
async def create_user_settings(
    key: Annotated[str, Path(min_length=1)],
    settings: Annotated[UserSettingsCreate, Body()],
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    user_settings = UserSettingsOrm(
        key=key, user=user_data.id, settings=settings.settings
    )

    try:
        session.add(user_settings)
        await session.flush()
        await session.refresh(user_settings)
        await session.commit()
    except IntegrityError as exc:
        if isinstance(exc.orig.__cause__, UniqueViolationError):
            raise HTTPException(
                status_code=409,
                detail="Settings for this user and module already exist!",
            )

    return UserSettingsResponse.model_validate(
        user_settings, from_attributes=True
    )


@router.put("/{key}", response_model=UserSettingsResponse)
async def update_user_settings(
    key: Annotated[str, Path(min_length=1)],
    settings: Annotated[UserSettingsUpdate, Body()],
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
) -> UserSettingsResponse:
    # get settings instance from database
    query = select(UserSettingsOrm).where(
        and_(UserSettingsOrm.key == key, UserSettingsOrm.user == user_data.id)
    )
    user_settings = await session.execute(query)
    user_settings = user_settings.scalar()

    if not user_settings:
        raise HTTPException(
            status_code=404, detail="Settings with given id not exist!"
        )

    user_settings.settings = settings.settings
    session.add(user_settings)
    await session.flush()
    await session.refresh(user_settings)
    await session.commit()

    return UserSettingsResponse.model_validate(
        user_settings, from_attributes=True
    )


@router.delete("/{key}", status_code=204)
async def delete_user_settings(
    key: Annotated[str, Path(min_length=1)],
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    # get settings instance from database
    query = select(UserSettingsOrm).where(
        and_(UserSettingsOrm.key == key, UserSettingsOrm.user == user_data.id)
    )
    user_settings = await session.execute(query)
    user_settings = user_settings.scalar()

    if not user_settings:
        raise HTTPException(
            status_code=404, detail="Settings with given id not exist!"
        )

    await session.delete(user_settings)
    await session.commit()
