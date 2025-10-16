from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from v1.controllers.exceptions.base import ControllerException
from v1.controllers.module_settings.common.create.create_handler import (
    ModuleSettingsCreateHandler,
)
from v1.controllers.module_settings.common.delete.delete_handler import (
    ModuleSettingsDeleteHandler,
)
from v1.controllers.module_settings.common.input_models.models import (
    ModelSettingsCreteModel,
    ModelSettingsUpdateModel,
)
from v1.controllers.module_settings.common.output_models.models import (
    ModelSettingsOutput,
)
from v1.controllers.module_settings.common.update.update_handler import (
    ModuleSettingsUpdateHandler,
)
from v1.database.database import Database
from v1.database.models.modules import ModuleSettings
from v1.routers.module_settings.models import ModelSettingsInfo
from v1.routers.module_settings.utils import (
    get_module_by_name_or_raise_error,
    get_module_settings_or_raise_error,
)
from v1.security.security_data_models import UserData
from v1.security.security_factory import security

router = APIRouter(prefix="/module_settings", tags=["Module Settings"])


@router.get("", status_code=200, response_model=List[ModelSettingsInfo])
async def read_module_settings(
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    """Returns settings for all modules"""
    stmt = select(ModuleSettings)
    all_settings = await session.execute(stmt)
    all_settings = all_settings.scalars().all()
    return all_settings


@router.post("", status_code=201, response_model=ModelSettingsOutput)
async def create_module_settings(
    module_settings: ModelSettingsCreteModel,
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """Creates settings for a specific model"""

    create_handler = ModuleSettingsCreateHandler(
        moduls_settings=[module_settings],
        session=session,
        user_name=user_data.name,
    )
    try:
        res = await create_handler.create_with_commit()
    except ControllerException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return res[0]


@router.get("/{module_name}", status_code=200, response_model=ModelSettingsInfo)
async def read_settings_of_particular_module(
    module_name: str,
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    """Returns settings for a specific module"""
    await get_module_by_name_or_raise_error(
        module_name=module_name, session=session
    )

    module_settings = await get_module_settings_or_raise_error(
        module_name=module_name, session=session
    )

    return module_settings


@router.put(
    "/{module_name}", status_code=200, response_model=ModelSettingsOutput
)
async def update_settings_of_particular_module(
    module_settings: ModelSettingsUpdateModel,
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """Full update of settings for a specific module"""

    update_handler = ModuleSettingsUpdateHandler(
        new_moduls_settings=[module_settings],
        session=session,
        user_name=user_data.name,
    )
    try:
        res = await update_handler.update_with_commit()
    except ControllerException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return res[0]


@router.delete("/{module_name}", status_code=204)
async def delete_settings_of_particular_module(
    module_name: str,
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    """Deletes settings for a specific module"""

    delete_handler = ModuleSettingsDeleteHandler(
        modul_names=[module_name], session=session, user_name=user_data.name
    )

    try:
        await delete_handler.delete_with_commit()
    except ControllerException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return {"status": "Successfully deleted"}
