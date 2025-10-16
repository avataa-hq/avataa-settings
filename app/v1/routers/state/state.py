from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from v1 import settings
from v1.database.database import Database
from v1.database.models.state import State
from v1.security.security_data_models import UserData
from v1.security.security_factory import security

router = APIRouter(prefix="/state", tags=["state"])


@router.post("/", response_model=UUID4)
async def save_state(
    state: dict = Body(...),
    expires_in_minutes: int = Body(..., ge=0),
    session: AsyncSession = Depends(Database().get_session_with_depends),
    user_data: UserData = Depends(security),
):
    if 0 < settings.EXPIRES_IN_MINUTES_LIMIT < expires_in_minutes:
        raise HTTPException(
            status_code=422,
            detail=f"Limit exceeded. Maximum allowable value {settings.EXPIRES_IN_MINUTES_LIMIT}",
        )

    now = datetime.now()
    expire = (
        (now + timedelta(minutes=expires_in_minutes))
        if expires_in_minutes > 0
        else None
    )
    db_state = State(
        value=state,
        creation_date=now,
        expire_date=expire,
        created_by=user_data.name,
    )
    session.add(db_state)
    await session.flush()
    await session.refresh(db_state)
    await session.commit()
    return db_state.id


@router.get("/{stateId}", response_model=dict)
async def get_state(
    state_id: UUID4 = Path(..., alias="stateId"),
    session: AsyncSession = Depends(Database().get_session_with_depends),
):
    state: State | None = await session.get(State, state_id)
    now = datetime.now()
    if state is None or state.expire_date < now:
        raise HTTPException(status_code=404, detail="State not found")
    return state.value
