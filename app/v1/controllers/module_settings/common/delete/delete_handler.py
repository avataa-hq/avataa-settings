import math
from typing import List, Generator

from sqlalchemy.ext.asyncio import AsyncSession

from v1.controllers.exceptions.base import ControllerException
from v1.controllers.module_settings.common.get.utils import (
    get_modules_settings_by_names,
)
from v1.controllers.module_settings_logs.common.builder.msl_builder import (
    ModuleSettingsLogsBuilder,
)
from v1.settings import POSTGRES_ITEMS_LIMIT_IN_QUERY


class ModuleSettingsDeleteHandler:
    def __init__(
        self,
        modul_names: List[str],
        session: AsyncSession,
        user_name: str = "admin",
    ):
        self.modul_names_to_delete = modul_names
        self.session = session
        self.user_name = user_name

    def __get_generator_of_module_names_to_delete_divided_on_parts(
        self,
    ) -> Generator:
        """Divides nodes_to_delete on parts and returns as generator"""
        size_per_step = POSTGRES_ITEMS_LIMIT_IN_QUERY
        steps = math.ceil(
            len(self.modul_names_to_delete) / POSTGRES_ITEMS_LIMIT_IN_QUERY
        )
        return (
            self.modul_names_to_delete[
                (start := step * size_per_step) : start + size_per_step
            ]
            for step in range(steps)
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

    async def __validate(self) -> None:
        """Raises ControllerException if can`t delete operation is not valid"""

        for (
            module_names
        ) in self.__get_generator_of_module_names_to_delete_divided_on_parts():
            await self.__check_if_module_settings_with_specific_names_exist(
                module_names
            )

    async def delete_without_commit(self) -> None:
        """Marks ModuleSettings as to_delete in the session, adds ModuleSettingsLogs to the session
        without saving changes in the database"""

        await self.__validate()

        for (
            module_names
        ) in self.__get_generator_of_module_names_to_delete_divided_on_parts():
            existing_modul_settings = await get_modules_settings_by_names(
                module_names, session=self.session
            )

            for module_settings in existing_modul_settings:
                # add logs
                logs = ModuleSettingsLogsBuilder(
                    module_name=module_settings.module_name,
                    settings_before=module_settings.settings,
                    modified_by_user=self.user_name,
                )
                for log in logs.get_list_of_msl_instance():
                    await self.session.delete(log)

                await self.session.delete(module_settings)

    async def delete_with_commit(self) -> None:
        """Deletes ModuleSettings adds ModuleSettingsLogs to the session
        with saving changes in the database"""
        await self.delete_without_commit()
        await self.session.commit()
