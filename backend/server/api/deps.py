from fastapi import Depends
from ..db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession


def db_session(session: AsyncSession = Depends(get_session)) -> AsyncSession:
    return session
