from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import internal, public
from app.db.session import engine
from app.models.base import Base

app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(internal.router, prefix=f"{settings.API_V1_STR}/internal", tags=["internal"])
app.include_router(public.router, prefix=f"{settings.API_V1_STR}/public", tags=["public"])

@app.on_event("startup")
async def startup_event():
    # Initialize DB (For dev only. In production, use Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
def health_check():
    return {"status": "ok"}
