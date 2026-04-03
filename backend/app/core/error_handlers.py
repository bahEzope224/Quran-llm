import uuid
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import BaseAppException

async def global_exception_handler(request: Request, exc: Exception):
    """Handler global pour les exceptions non capturees."""
    error_id = str(uuid.uuid4())
    
    # Tentative de recuperation de l'utilisateur (si authentifie via Clerk)
    user_id = "anonymous"
    if hasattr(request.state, "user"):
        user_id = getattr(request.state.user, "id", user_id)

    # Formatage de la reponse
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "error_id": error_id,
            "message": "Une erreur interne imprevue est survenue.",
            "location": "global_handler",
            "type": "INTERNAL_SERVER_ERROR",
            "user_id": user_id
        }
    )

async def app_exception_handler(request: Request, exc: BaseAppException):
    """Handler pour nos exceptions personnalisees."""
    error_id = str(uuid.uuid4())
    
    user_id = "anonymous"
    if hasattr(request.state, "user"):
        user_id = getattr(request.state.user, "id", user_id)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_id": error_id,
            "message": exc.message,
            "location": exc.location,
            "type": exc.__class__.__name__,
            "user_id": user_id,
            "details": exc.details
        }
    )
