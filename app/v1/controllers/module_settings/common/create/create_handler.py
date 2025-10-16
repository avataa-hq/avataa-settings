from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from v1.controllers.exceptions.base import ControllerException
from v1.controllers.module.common.get.utils import get_modules_by_names
from v1.controllers.module_settings.common.get.utils import (
    get_modules_settings_by_names,
)
from v1.controllers.module_settings.common.input_models.models import (
    ModelSettingsCreteModel,
)
from v1.controllers.module_settings_logs.common.builder.msl_builder import (
    ModuleSettingsLogsBuilder,
)
from v1.database.models.modules import ModuleSettings


class ModuleSettingsCreateHandler:
    def __init__(
        self,
        moduls_settings: List[dict] | List[ModelSettingsCreteModel],
        session: AsyncSession,
        user_name: str = "admin",
    ):
        self.new_moduls_settings = moduls_settings
        self.session = session
        self.user_name = user_name

    @property
    def new_moduls_settings(self):
        return self._new_moduls_settings

    @new_moduls_settings.setter
    def new_moduls_settings(self, v):
        for one_m_settings in v:
            if isinstance(one_m_settings, ModelSettingsCreteModel):
                continue
            else:
                ModelSettingsCreteModel.model_validate(one_m_settings)
        self._new_moduls_settings = v

    async def __check_if_module_with_specific_names_exist(
        self, module_names: List[str]
    ) -> None:
        """Raises ControllerException if modules with module_names do not exist"""
        existing_modules = await get_modules_by_names(
            module_names=module_names, session=self.session
        )

        if len(module_names) != len(existing_modules):
            not_exist = set(module_names).difference(
                {module_item.name for module_item in existing_modules}
            )

            raise ControllerException(
                status_code=404,
                detail=f"Modules with the following names do not exist: {list(not_exist)}.",
            )

    async def __check_if_module_settings_with_specific_names_exist(
        self, module_names: List[str]
    ) -> None:
        """Raises ControllerException if module_settings with module_names exist"""
        existing_modules_settings = await get_modules_settings_by_names(
            module_names=module_names, session=self.session
        )
        if len(existing_modules_settings) > 0:
            already_exist = [
                module_s.module_name for module_s in existing_modules_settings
            ]

            raise ControllerException(
                status_code=404,
                detail="Module Settings for Modules with names:"
                f" {list(already_exist)} already exist",
            )

    async def __validate(self) -> None:
        """Raises ControllerException if can`t create Module Settings"""
        unique_modul_names = list(
            {
                module_settings.module_name
                for module_settings in self.new_moduls_settings
            }
        )

        if unique_modul_names:
            await self.__check_if_module_with_specific_names_exist(
                unique_modul_names
            )
            await self.__check_if_module_settings_with_specific_names_exist(
                unique_modul_names
            )

    async def create_without_commit(self) -> List[ModuleSettings]:
        """Creates ModuleSettings adds ModuleSettings and ModuleSettingsLogs to the session
        and returns list of created ModuleSettings without saving in the database"""
        await self.__validate()
        res = []
        for new_modul_settings in self.new_moduls_settings:
            ms = ModuleSettings(**new_modul_settings.model_dump())
            self.session.add(ms)
            # add logs
            logs = ModuleSettingsLogsBuilder(
                module_name=ms.module_name,
                settings_after=ms.settings,
                modified_by_user=self.user_name,
            )
            for log in logs.get_list_of_msl_instance():
                self.session.add(log)

            res.append(ms)
        await self.session.flush()
        return res

    async def create_with_commit(self) -> List[ModuleSettings]:
        """Creates ModuleSettings adds ModuleSettings and ModuleSettingsLogs to the session
        and returns list of created ModuleSettings with saving all changes in the database"""
        res = await self.create_without_commit()
        await self.session.commit()
        return res
