from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import register_tortoise
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import os
import logging

from app.core.database import TORTOISE_ORM
from app.core.auth import get_current_user
from app.core.limiter import limiter
from app.routers import geography, company, project, user, document, asset, commissioning, upload, billing, workorder, wo_types, system, auth

load_dotenv()

logger = logging.getLogger(__name__)

_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",")]

app = FastAPI(
    title="ConstructIQ API",
    description="Project Management Built for Construction",
    version="1.0.0",
)

# --- Rate limiter ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception handlers ---

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Return the first error message in a simple format
    errors = exc.errors()
    detail = errors[0].get("msg", "Validation error") if errors else "Validation error"
    return JSONResponse(
        status_code=422,
        content={"detail": detail, "errors": errors},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# --- Routers ---
protected = {"dependencies": [Depends(get_current_user)]}

app.include_router(auth.router, prefix="/api/v1")  # unprotected
app.include_router(geography.router, prefix="/api/v1", **protected)
app.include_router(company.router, prefix="/api/v1", **protected)
app.include_router(project.router, prefix="/api/v1", **protected)
app.include_router(user.router, prefix="/api/v1", **protected)
app.include_router(document.router, prefix="/api/v1", **protected)
app.include_router(asset.router, prefix="/api/v1", **protected)
app.include_router(commissioning.router, prefix="/api/v1", **protected)
app.include_router(wo_types.router, prefix="/api/v1", **protected)
app.include_router(workorder.router, prefix="/api/v1", **protected)
app.include_router(system.router, prefix="/api/v1", **protected)
app.include_router(upload.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1", dependencies=[])

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)


@app.get("/")
async def root():
    return {"message": "ConstructIQ API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
