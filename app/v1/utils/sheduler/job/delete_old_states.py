import datetime
from datetime import timedelta

from sqlalchemy import delete

from v1 import settings
from v1.database.database import Database
from v1.database.models.state import State


async def delete_old_states():
    now = datetime.datetime.now()
    expire_date = now - timedelta(minutes=settings.DROP_INTERVAL_MINUTES)
    query = delete(State).where(State.expire_date <= expire_date)
    async for session in Database().get_session():
        await session.execute(query)
        await session.commit()
