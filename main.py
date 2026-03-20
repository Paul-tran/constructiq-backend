from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv
import os

from app.core.database import TORTOISE_ORM
from app.core.auth import get_current_user
from app.routers import geography, company, project, user, document, asset, commissioning, upload

load_dotenv()

# ALLOWED_ORIGINS is comma-separated in production, e.g. "https://yourapp.vercel.app,https://www.yourapp.com"
_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",")]

app = FastAPI(
    title="ConstructIQ API",
    description="Project Management Built for Construction",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

protected = {"dependencies": [Depends(get_current_user)]}

app.include_router(geography.router, prefix="/api/v1", **protected)
app.include_router(company.router, prefix="/api/v1", **protected)
app.include_router(project.router, prefix="/api/v1", **protected)
app.include_router(user.router, prefix="/api/v1", **protected)
app.include_router(document.router, prefix="/api/v1", **protected)
app.include_router(asset.router, prefix="/api/v1", **protected)
app.include_router(commissioning.router, prefix="/api/v1", **protected)
app.include_router(upload.router, prefix="/api/v1")

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
