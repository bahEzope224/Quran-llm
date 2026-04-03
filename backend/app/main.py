from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.user import router as user_router


from app.routes.admin import router as admin_router


from app.core.exceptions import BaseAppException
from app.core.error_handlers import global_exception_handler, app_exception_handler

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)

# Handlers d'erreurs
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(BaseAppException, app_exception_handler)

# Ajout du handler pour les exceptions natives de FastAPI pour injecter CORS
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    from fastapi.responses import JSONResponse
    origin = request.headers.get("origin")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True, "type": "HTTPException"},
        headers={
            "Access-Control-Allow-Origin": origin if origin else "*",
            "Access-Control-Allow-Credentials": "true" if origin else "false"
        }
    )

# Nettoyage des origines pour eviter les espaces ou slashs parasites
allowed_origins = [o.strip().rstrip("/") for o in settings.frontend_origins if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "healthy"}
