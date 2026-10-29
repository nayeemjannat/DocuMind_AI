from fastapi import APIRouter, Depends
from app.core.security import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=AuthenticatedUser)
async def get_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Return currently authenticated user information."""
    return current_user
