from datetime import datetime, timedelta, timezone
import jwt
from typing import Any, Dict
from ..core.config import settings

ALGO = "HS256"


def create_jwt(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": now + timedelta(minutes=settings.JWT_EXPIRES_MIN),
        "iat": now,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGO)
