import asyncio
import json
import logging

import grpc
from grpc.aio import Channel

from frontend_settings_proto import frontend_settings_pb2
from frontend_settings_proto import frontend_settings_pb2_grpc


async def set_default_palette(channel: Channel):
    stub = frontend_settings_pb2_grpc.FrontendSettingsStub(channel)

    preference = frontend_settings_pb2.PreferenceInstance(
        preference_name="some_pref", val_type="float", kpi_id=1
    )

    preferences = frontend_settings_pb2.PreferenceInstances(
        preference_instances=[preference]
    )

    msg = frontend_settings_pb2.RequestObjectForPalette(
        tmo_id_preference={1: preferences}
    )
    grpc_response = await stub.SetDefaultPaletteForItems(msg)
    print(grpc_response.wrong_kpi_ids)


async def set_custom_palette(channel: Channel):
    stub = frontend_settings_pb2_grpc.FrontendSettingsStub(channel)

    preference_instance = (
        frontend_settings_pb2.PreferenceInstanceForWithPalette(
            preference_name="string",
            val_type="float",
            kpi_id=1,
            palette=json.dumps({"a": 3}),
            object_type_id=1,
        )
    )

    msg = frontend_settings_pb2.RequestToSetCustomPalette(
        preference_instances=[preference_instance]
    )

    grpc_response = await stub.SetCustomColorRangeForKPI(msg)
    print(grpc_response.wrong_kpi_ids)


async def main():
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        # await set_default_palette(channel=channel)
        await set_custom_palette(channel=channel)


if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(main())
