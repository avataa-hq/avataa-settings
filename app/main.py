from starlette.middleware.cors import CORSMiddleware

import settings
from init_app import create_app, lifespan
from v1.routers.color_range import color_range as color_range_new
from v1.routers.map import color_range
from v1.routers.modules import modules
from v1.routers.module_setting_logs.routers import (
    router as module_settings_logs_router,
)
from v1.routers.module_settings.routers import router as module_settings_router
from v1.routers.object_params import object_params
from v1.routers.process import process
from v1.routers.state import state
from v1.routers.table import columns, filters
from v1.routers.user_settings import user_settings

"""
The code below is responsible for setting up the entire microservice before running.
Prefix sets the main prefix for the entire microservice.

"""

APP_VERSION = "1"

app = create_app(root_path=settings.PREFIX, lifespan=lifespan)

if settings.DEBUG:
    """
    In case of debug mode, it sets access with any login parameters
    """
    app.debug = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

"""
Configuration block of the first version of the microservice.
The service is created and the endpoints are connected, as well as mounted into the main application
"""

v1_options = {
    "root_path": f"{settings.PREFIX}/v{APP_VERSION}",
    "title": settings.TITLE,
    "version": APP_VERSION,
}


if settings.DEBUG:
    v1_options["debug"] = True

app_v1 = create_app(**v1_options)

app_v1.include_router(filters.router)
app_v1.include_router(columns.router)
app_v1.include_router(color_range.router)
app_v1.include_router(object_params.router)
app_v1.include_router(modules.router)
app_v1.include_router(process.router)
app_v1.include_router(state.router)
app_v1.include_router(color_range_new.router)
app_v1.include_router(module_settings_router)
app_v1.include_router(user_settings.router)
app_v1.include_router(module_settings_logs_router)

app.mount("/v1", app_v1)
