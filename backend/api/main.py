from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth_routes import router as auth_router
from api.google_routes import router as google_router
from api.routes import router
from api.setup_routes import router as setup_router
from api.health_routes import router as health_router
from config.settings import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(google_router, prefix=settings.api_prefix)
app.include_router(setup_router, prefix=settings.api_prefix)
app.include_router(health_router)


@app.get("/")
def root() -> dict:
    return {
        "name": settings.app_name,
        "status": "ok",
        "docs": "/docs",
        "api_base": settings.api_prefix,
    }
