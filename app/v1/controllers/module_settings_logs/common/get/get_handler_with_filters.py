from typing import List, Sequence

from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from v1.controllers.module_settings_logs.common.input_models.models import (
    MSLFilterInput,
    MSLSortDirections,
    MSLSortBy,
)
from v1.controllers.module_settings_logs.common.output_models.models import (
    MSLOutput,
)
from v1.database.models.modules import ModuleSettingsLogs, Module


class MSLFilterHandler:
    def __init__(
        self, filter_conditions: MSLFilterInput, session: AsyncSession
    ):
        self.filter_conditions = filter_conditions
        self.session = session

    def __get_and_condition_for_filter_module_names(self) -> List:
        res = list()
        if self.filter_conditions.module_names:
            res = [Module.custom_name.in_(self.filter_conditions.module_names)]
        return res

    def __get_and_condition_for_filter_fields_keys(self) -> List:
        res = list()
        if self.filter_conditions.fields_keys:
            res.append(
                ModuleSettingsLogs.variable.in_(
                    self.filter_conditions.fields_keys
                )
            )
        return res

    def __get_and_condition_for_filter_from_date(self) -> List:
        res = list()
        if self.filter_conditions.from_date:
            res.append(
                ModuleSettingsLogs.change_time
                >= self.filter_conditions.from_date
            )
        return res

    def __get_and_condition_for_filter_to_date(self) -> List:
        res = list()
        if self.filter_conditions.to_date:
            res.append(
                ModuleSettingsLogs.change_time <= self.filter_conditions.to_date
            )
        return res

    def __get_and_condition_for_users(self) -> List:
        res = list()
        if self.filter_conditions.users:
            res.append(
                ModuleSettingsLogs.user.in_(self.filter_conditions.users)
            )
        return res

    def __get_and_condition_for_old_value(self) -> List:
        res = list()
        if self.filter_conditions.old_value:
            res.append(
                ModuleSettingsLogs.old_value == self.filter_conditions.old_value
            )
        return res

    def __get_and_condition_for_new_value(self) -> List:
        res = list()
        if self.filter_conditions.new_value:
            res.append(
                ModuleSettingsLogs.user == self.filter_conditions.new_value
            )
        return res

    def __get_sort_conditions(self) -> None | List:
        if not self.filter_conditions.sort_by:
            return None
        res = []
        for sort_cond in self.filter_conditions.sort_by:
            if sort_cond.sort_by == MSLSortBy.DOMAIN:
                sort_field = Module.custom_name
            else:
                sort_field = getattr(
                    ModuleSettingsLogs, sort_cond.sort_by, None
                )
            if not sort_field:
                continue

            if sort_cond.sort_direction == MSLSortDirections.ASC.value:
                res.append(asc(sort_field))
            else:
                res.append(desc(sort_field))
        return res

    def __get_all_where_conditions(self) -> List:
        where_conditions = (
            self.__get_and_condition_for_filter_module_names()
            + self.__get_and_condition_for_filter_fields_keys()
            + self.__get_and_condition_for_filter_from_date()
            + self.__get_and_condition_for_filter_to_date()
            + self.__get_and_condition_for_users()
            + self.__get_and_condition_for_old_value()
            + self.__get_and_condition_for_new_value()
        )
        return where_conditions

    def __create_search_stmt(self):
        where_conditions = self.__get_all_where_conditions()

        stmt = (
            select(
                Module.custom_name.label("domain"),
                ModuleSettingsLogs.variable,
                ModuleSettingsLogs.user,
                ModuleSettingsLogs.change_time,
                ModuleSettingsLogs.old_value,
                ModuleSettingsLogs.new_value,
            )
            .join(ModuleSettingsLogs, Module.name == ModuleSettingsLogs.domain)
            .where(*where_conditions)
        )

        if self.filter_conditions.limit:
            stmt = stmt.limit(self.filter_conditions.limit)

        if self.filter_conditions.offset:
            stmt = stmt.offset(self.filter_conditions.offset)

        sort_cond = self.__get_sort_conditions()
        if sort_cond:
            stmt = stmt.order_by(*sort_cond)
        return stmt

    def __create_count_stmt(self):
        where_conditions = self.__get_all_where_conditions()

        stmt = (
            select(count(ModuleSettingsLogs.id))
            .join(Module, Module.name == ModuleSettingsLogs.domain)
            .where(*where_conditions)
        )
        return stmt

    async def get_count(self):
        stmt = self.__create_count_stmt()
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_results(self) -> Sequence[MSLOutput]:
        stmt = self.__create_search_stmt()
        res = await self.session.execute(stmt)
        res = [MSLOutput.from_orm(item) for item in res.all()]
        return res
