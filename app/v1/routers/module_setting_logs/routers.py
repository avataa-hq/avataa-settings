from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from v1.controllers.module_settings_logs.common.get.get_handler_with_filters import (
    MSLFilterHandler,
)
from v1.controllers.module_settings_logs.common.input_models.models import (
    MSLFilterInput,
)
from v1.controllers.module_settings_logs.common.output_models.models import (
    MSLOutput,
    MSLPaginationOutput,
    MSLPaginationMeta,
)
from v1.database.database import Database


router = APIRouter(
    prefix="/module_settings_logs", tags=["Module Settings Logs"]
)


@router.post(
    "/get_msl_by_filters", status_code=200, response_model=MSLPaginationOutput
)
async def get_filtered_module_settings_logs(
    filter_conditions: MSLFilterInput,
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    """Returns module settings logs matched the filter_conditions"""

    filter_handler = MSLFilterHandler(
        filter_conditions=filter_conditions, session=session
    )
    elements = [
        MSLOutput.from_orm(item) for item in await filter_handler.get_results()
    ]
    count = await filter_handler.get_count()

    meta = MSLPaginationMeta(total_count=count, page_count=len(elements))

    return MSLPaginationOutput(meta=meta, elements=elements)
