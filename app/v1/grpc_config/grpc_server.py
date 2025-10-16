"""Async gRPC server"""

import asyncio
import json
import logging

import grpc

from v1.database import Base
from v1.database.database import Database
from v1.database.models.color_range import ColorRangeTableNew
from v1.grpc_config.grpc_utils import check_color_range_exists
from v1.routers.color_range.models import ColorRangeCreate
from .frontend_settings_proto import frontend_settings_pb2
from .frontend_settings_proto import frontend_settings_pb2_grpc
from v1.settings import DATABASE_URL, DB_SCHEMA


class FrontendSettings(frontend_settings_pb2_grpc.FrontendSettingsServicer):
    async def SetDefaultPaletteForItems(
        self,
        request: frontend_settings_pb2.RequestObjectForPalette,
        context: grpc.ServicerContext,
    ) -> frontend_settings_pb2.WrongKpiIds:
        DEFAULT_PALLETE = {
            "colors": [
                {"name": "Tier 1", "id": 1, "hex": "#FF0000"},
                {"name": "Tier 2", "id": 2, "hex": "#FFCC00"},
                {"name": "Tier 3", "id": 3, "hex": "#66CC33"},
            ]
        }

        wrong_kpi_ids = []
        db = Database()
        db.set_config(
            database_url=DATABASE_URL,
            db_schema=DB_SCHEMA,
            metadata=Base.metadata,
        )

        async for session in db.get_session():
            for (
                tmo_id,
                preference_instances,
            ) in request.tmo_id_preference.items():
                for (
                    preference_instance
                ) in preference_instances.preference_instances:
                    kpi_id = preference_instance.kpi_id
                    preference_name = preference_instance.preference_name
                    preference_val_type = preference_instance.val_type

                    try:
                        if preference_val_type in {"number", "float", "int"}:
                            DEFAULT_PALLETE["values"] = [20, 80]

                        data_settings = {
                            "direction": "asc",
                            "tmoId": str(tmo_id),
                            "tprmId": str(kpi_id),
                            "valType": preference_val_type,
                            "name": preference_name,
                            "public": True,
                            "default": False,
                            "withIndeterminate": True,
                            "withCleared": True,
                            "value_type": "General",
                            "ranges": DEFAULT_PALLETE,
                        }
                        data_settings = ColorRangeCreate(**data_settings)

                        color_range_exists = await check_color_range_exists(
                            session=session,
                            tmo_id=str(tmo_id),
                            kpi_id=str(kpi_id),
                            color_range_name=preference_name,
                        )
                        if color_range_exists:
                            raise ValueError

                        orm_item = ColorRangeTableNew(
                            created_by="",
                            created_by_sub="",
                            **data_settings.model_dump(by_alias=False),
                        )
                        session.add(orm_item)

                    except BaseException as e:
                        print(e)
                        wrong_kpi_ids.append(kpi_id)
                        continue

            await session.commit()

        return frontend_settings_pb2.WrongKpiIds(wrong_kpi_ids=wrong_kpi_ids)

    async def SetCustomColorRangeForKPI(
        self,
        request: frontend_settings_pb2.RequestToSetCustomPalette,
        context: grpc.ServicerContext,
    ) -> frontend_settings_pb2.WrongKpiIds:
        wrong_kpi_ids = []
        db = Database()
        db.set_config(
            database_url=DATABASE_URL,
            db_schema=DB_SCHEMA,
            metadata=Base.metadata,
        )

        async for session in db.get_session():
            for preference_instance in request.preference_instances:
                kpi_id = preference_instance.kpi_id
                preference_name = preference_instance.preference_name
                preference_val_type = preference_instance.val_type
                kpi_object_type = preference_instance.object_type_id

                try:
                    data_settings = {
                        "direction": "asc",
                        "tmoId": str(kpi_object_type),
                        "tprmId": str(kpi_id),
                        "valType": preference_val_type,
                        "name": preference_name,
                        "public": True,
                        "default": False,
                        "withIndeterminate": True,
                        "withCleared": True,
                        "value_type": "General",
                        "ranges": json.loads(preference_instance.palette),
                    }

                    data_settings = ColorRangeCreate(**data_settings)

                    color_range_exists = await check_color_range_exists(
                        session=session,
                        tmo_id=str(kpi_object_type),
                        kpi_id=str(kpi_id),
                        color_range_name=preference_name,
                    )
                    if color_range_exists:
                        color_range_exists.ranges = json.loads(
                            preference_instance.palette
                        )
                        session.add(color_range_exists)

                    else:
                        orm_item = ColorRangeTableNew(
                            created_by="",
                            created_by_sub="",
                            **data_settings.model_dump(by_alias=False),
                        )
                        session.add(orm_item)

                except BaseException as e:
                    print(e)
                    wrong_kpi_ids.append(kpi_id)
                    continue

            await session.commit()

        return frontend_settings_pb2.WrongKpiIds(wrong_kpi_ids=wrong_kpi_ids)


async def start_grpc_serve() -> None:
    server = grpc.aio.server()
    frontend_settings_pb2_grpc.add_FrontendSettingsServicer_to_server(
        FrontendSettings(), server
    )
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_grpc_serve())
