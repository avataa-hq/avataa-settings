from datetime import datetime
from typing import List

from v1.controllers.module_settings_logs.common.builder.utils import (
    create_one_level_dict_from_multilayer_dict,
)
from v1.database.models.modules import ModuleSettingsLogs


class ModuleSettingsLogsBuilder:
    def __init__(
        self,
        module_name: str,
        modified_by_user: str,
        settings_before: dict = None,
        settings_after: dict = None,
    ):
        self.module_name = module_name
        self.settings_before = settings_before if settings_before else dict()
        self.settings_after = settings_after if settings_after else dict()
        self.modified_by_user = modified_by_user

    def get_list_of_msl_instance(self) -> List[ModuleSettingsLogs]:
        result = list()
        one_level_dict_before = create_one_level_dict_from_multilayer_dict(
            self.settings_before
        )
        one_level_dict_after = create_one_level_dict_from_multilayer_dict(
            self.settings_after
        )
        change_time = datetime.utcnow()
        for k, v in one_level_dict_before.items():
            if k not in one_level_dict_after:
                msl = ModuleSettingsLogs(
                    domain=self.module_name,
                    variable=k,
                    user=self.modified_by_user,
                    change_time=change_time,
                    old_value=str(v),
                    new_value=None,
                )
                result.append(msl)

            else:
                new_k_value = one_level_dict_after.get(k)
                if v != new_k_value:
                    msl = ModuleSettingsLogs(
                        domain=self.module_name,
                        variable=k,
                        user=self.modified_by_user,
                        change_time=change_time,
                        old_value=str(v),
                        new_value=str(new_k_value),
                    )
                    result.append(msl)

        # add new keys to results
        for k in one_level_dict_after.keys() - one_level_dict_before.keys():
            new_value = str(one_level_dict_after[k])
            msl = ModuleSettingsLogs(
                domain=self.module_name,
                variable=k,
                user=self.modified_by_user,
                change_time=change_time,
                old_value=None,
                new_value=new_value,
            )
            result.append(msl)
        return result
