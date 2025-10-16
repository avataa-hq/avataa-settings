import math
from typing import List, Generator

from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter
from v1.controllers.exceptions.base import ControllerException
from v1.controllers.module.common.get.utils import get_modules_by_names
from v1.controllers.module_settings.common.get.utils import (
    get_modules_settings_by_names,
)
from v1.controllers.module_settings.common.input_models.models import (
    ModelSettingsUpdateModel,
)
from v1.controllers.module_settings_logs.common.builder.msl_builder import (
    ModuleSettingsLogsBuilder,
)
from v1.database.models.modules import ModuleSettings

from v1.settings import POSTGRES_ITEMS_LIMIT_IN_QUERY


class ModuleSettingsUpdateHandler:
    def __init__(
        self,
        new_moduls_settings: List[dict] | List[ModelSettingsUpdateModel],
        session: AsyncSession,
        user_name: str = "admin",
    ):
        self.new_moduls_settings = new_moduls_settings
        self.session = session
        self.user_name = user_name

    @property
    def new_moduls_settings(self):
        return self._new_moduls_settings

    @new_moduls_settings.setter
    def new_moduls_settings(self, v):
        for one_m_settings in v:
            if isinstance(one_m_settings, ModelSettingsUpdateModel):
                continue
            else:
                ModelSettingsUpdateModel.model_validate(one_m_settings)
        self._new_moduls_settings = v

    def __get_generator_of_module_settings_to_update_divided_on_parts(
        self,
    ) -> Generator:
        """Divides new_moduls_settings on parts and returns as generator"""
        size_per_step = POSTGRES_ITEMS_LIMIT_IN_QUERY
        steps = math.ceil(
            len(self.new_moduls_settings) / POSTGRES_ITEMS_LIMIT_IN_QUERY
        )
        return (
            self.new_moduls_settings[
                (start := step * size_per_step) : start + size_per_step
            ]
            for step in range(steps)
        )

    @staticmethod
    def __get_module_names(
        module_settings: List[ModelSettingsUpdateModel],
    ) -> List[str]:
        """Returns list of module names"""
        return [module_s.module_name for module_s in module_settings]

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
                detail=f"Modules with names: {list(not_exist)} do not exist",
            )

    async def __check_if_module_settings_with_specific_names_exist(
        self, module_names: List[str]
    ) -> None:
        """Raises ControllerException if module_settings with module_names do not exist"""
        existing_modules_settings = await get_modules_settings_by_names(
            module_names=module_names, session=self.session
        )
        if len(module_names) != len(existing_modules_settings):
            not_exist = set(module_names).difference(
                {
                    module_item.module_name
                    for module_item in existing_modules_settings
                }
            )

            raise ControllerException(
                status_code=404,
                detail="Module Settings for Modules with names:"
                f" {list(not_exist)} do not exist",
            )

    @staticmethod
    def __get_module_name_duplications(module_names: List[str]) -> List[str]:
        """Returns list of duplicate module_names"""
        unique_modul_names = set(module_names)
        if len(unique_modul_names) != len(module_names):
            counted_m_names = Counter(module_names)
            return [k for k, v in counted_m_names.items() if v > 1]

    def __module_duplication_name_validation(
        self, module_names: List[str]
    ) -> None:
        """Raises ControllerException if duplicate module_names exist"""
        duplications = self.__get_module_name_duplications(module_names)
        if duplications:
            raise ControllerException(
                status_code=422,
                detail=f"There are duplications of module names: {duplications}",
            )

    async def __validate(self) -> None:
        """Raises ControllerException if can`t update ModuleSettings"""

        for list_of_m_settings in (
            self.__get_generator_of_module_settings_to_update_divided_on_parts()
        ):
            module_names = self.__get_module_names(list_of_m_settings)
            self.__module_duplication_name_validation(module_names)
            await self.__check_if_module_with_specific_names_exist(module_names)
            await self.__check_if_module_settings_with_specific_names_exist(
                module_names
            )

    async def update_without_commit(self) -> List[ModuleSettings]:
        """Updates ModuleSettings adds updated ModuleSettings and ModuleSettingsLogs to the session
        and returns list of updated ModuleSettings without saving in the database"""
        await self.__validate()
        res = []
        for list_of_m_settings in (
            self.__get_generator_of_module_settings_to_update_divided_on_parts()
        ):
            module_names = self.__get_module_names(list_of_m_settings)

            existing_modul_settings = await get_modules_settings_by_names(
                module_names, session=self.session
            )

            step_cache = {
                m_s.module_name: m_s for m_s in existing_modul_settings
            }

            for m_s_to_update in list_of_m_settings:
                ms_from_cache = step_cache.get(m_s_to_update.module_name)

                # add logs
                logs = ModuleSettingsLogsBuilder(
                    module_name=ms_from_cache.module_name,
                    settings_before=ms_from_cache.settings,
                    settings_after=m_s_to_update.settings,
                    modified_by_user=self.user_name,
                )

                ms_from_cache.settings = m_s_to_update.settings
                self.session.add(ms_from_cache)

                for log in logs.get_list_of_msl_instance():
                    self.session.add(log)

                res.append(ms_from_cache)
        return res

    async def update_with_commit(self) -> List[ModuleSettings]:
        """Updates ModuleSettings adds updated ModuleSettings and ModuleSettingsLogs to the session
        and returns list of updated ModuleSettings with saving all changes in the database"""
        res = await self.update_without_commit()
        await self.session.commit()
        return res
