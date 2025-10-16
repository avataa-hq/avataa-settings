"""
The class for connecting to the database.
Use init_database to create a database connection once at the start.
Use get_session every time you send a new query to the database.
"""

import asyncio
import traceback
from sys import stderr
from typing import AsyncIterator

from fastapi import HTTPException, status, Depends
from sqlalchemy import false
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)


from fastapi.requests import Request

from v1.security.security_data_models import UserData
from v1.security.security_factory import security
from v1.utils.singleton import Singleton

ACTIONS = {
    "POST": "create",
    "GET": "read",
    "PATH": "update",
    "PUT": "update",
    "DELETE": "delete",
}


class Database(metaclass=Singleton):
    def __init__(self):
        self._url = None
        self.engine = None
        self.async_session = None
        self._metadata = None
        self._schema = None

    def set_config(self, database_url: str, db_schema: str, metadata):
        self._url = database_url
        self._metadata = metadata
        self._schema = db_schema

    async def init(self):
        try:
            self.engine = create_async_engine(
                self._url,
                echo=False,
                future=True,
                pool_pre_ping=True,
                connect_args={
                    "server_settings": {
                        "application_name": "Frontend Settings MS",
                        "search_path": self._schema,
                    },
                },
            )
            async_session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
            self.async_session = async_scoped_session(
                async_session_factory, scopefunc=asyncio.current_task
            )
            async with self.engine.begin() as connection:
                await connection.run_sync(self._metadata.create_all)
        except Exception as e:
            print(traceback.format_exception(e), file=stderr)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error.",
            )

    async def get_session(
        self,
        request: Request | None = None,
        user_data: UserData | None = None,
    ) -> AsyncIterator[AsyncSession]:
        if self.engine is None:
            await self.init()
        async with self.async_session() as session:
            if user_data and request:
                session.info["jwt"] = user_data
                session.info["action"] = [ACTIONS.get(request.method, false())]
            yield session

    async def get_session_with_depends(
        self,
        request: Request,
        user_data: UserData = Depends(security),
    ) -> AsyncIterator[AsyncSession]:
        if self.engine is None:
            await self.init()
        async with self.async_session() as session:
            session.info["jwt"] = user_data
            session.info["action"] = [ACTIONS.get(request.method, false())]
            yield session
