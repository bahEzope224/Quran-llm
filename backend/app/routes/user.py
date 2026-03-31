from fastapi import APIRouter

from app.models.schemas import UserProfileResponse


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile() -> UserProfileResponse:
    return UserProfileResponse(
        name="Ibrahima Bah",
        avatar_initials="IB",
        legal_school="Maliki",
        language="Francais",
        mode="Clair",
        notifications_enabled=True,
    )
