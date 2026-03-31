from fastapi import APIRouter, Header


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status")
async def auth_status() -> dict[str, str]:
    return {
        "provider": "clerk",
        "status": "ready",
    }


@router.get("/me")
async def auth_me(authorization: str | None = Header(default=None)) -> dict[str, str | bool]:
    return {
        "provider": "clerk",
        "authenticated": bool(authorization),
        "message": (
            "Ajoutez la verification du token Clerk ici cote backend."
            if authorization
            else "Aucun token d'authorization fourni."
        ),
    }
