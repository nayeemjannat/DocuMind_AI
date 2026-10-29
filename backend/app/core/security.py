import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.core.config import settings

# HTTP Bearer scheme
bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Authenticated user context extracted from verified JWT."""
    id: uuid.UUID
    email: Optional[str] = None
    role: str = "authenticated"


def create_test_token(
    user_id: uuid.UUID,
    email: str = "test@example.com",
    expires_in_minutes: int = 60,
    secret: Optional[str] = None,
) -> str:
    """Generate a signed JWT for testing."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_in_minutes)).timestamp()),
    }
    jwt_secret = secret or settings.SUPABASE_JWT_SECRET
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


def verify_token(token: str) -> AuthenticatedUser:
    """Verify Supabase JWT token and extract authenticated user identity."""
    try:
        # Decode token with Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},  # aud can be configured if needed
        )
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject (user ID)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token contains invalid user ID format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return AuthenticatedUser(
            id=user_id,
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthenticatedUser:
    """FastAPI dependency: verifies bearer token from Authorization header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_token(credentials.credentials)
