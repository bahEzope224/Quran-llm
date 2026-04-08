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
    "accepted_privacy": False,
    "accepted_cgu": False,
}


def _snapshot_profile() -> UserProfileResponse:
    return UserProfileResponse(
        name=_PROFILE_STATE.get("name", ""),
        avatar_initials=_PROFILE_STATE.get("avatar_initials", ""),
        legal_school=_PROFILE_STATE.get("legal_school", ""),
        language=_PROFILE_STATE.get("language", ""),
        mode=_PROFILE_STATE.get("mode", ""),
        notifications_enabled=_PROFILE_STATE.get("notifications_enabled", True),
        accepted_privacy=_PROFILE_STATE.get("accepted_privacy", False),
        accepted_cgu=_PROFILE_STATE.get("accepted_cgu", False),
    )


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
        accepted_privacy=profile.accepted_privacy,
        accepted_cgu=profile.accepted_cgu,
    )
    return _snapshot_profile()
