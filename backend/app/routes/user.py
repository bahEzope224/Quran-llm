from fastapi import APIRouter

from app.models.schemas import UserProfile, UserProfileResponse


router = APIRouter(prefix="/user", tags=["user"])

_PROFILE_STATE = {
    "name": "Ibrahima Bah",
    "avatar_initials": "IB",
    "legal_school": "Maliki",
    "language": "Francais",
    "mode": "Clair",
    "notifications_enabled": True,
}


def _snapshot_profile() -> UserProfileResponse:
    return UserProfileResponse(**_PROFILE_STATE)


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile() -> UserProfileResponse:
    return _snapshot_profile()


@router.patch("/profile", response_model=UserProfileResponse)
async def update_profile(profile: UserProfile) -> UserProfileResponse:
    _PROFILE_STATE.update(
        legal_school=profile.legal_school,
        language=profile.language,
        mode=profile.mode,
        notifications_enabled=profile.notifications_enabled,
    )
    return _snapshot_profile()
