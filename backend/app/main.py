from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models import Base  # noqa: F401 — 모든 모델 등록
from app.api.routes import health, locations, groups, assets, catalogs, persons, reports, evtx, form_templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="설비관리 시스템 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,    prefix="/api")
app.include_router(locations.router, prefix="/api/locations",  tags=["locations"])
app.include_router(groups.router,    prefix="/api/groups",     tags=["groups"])
app.include_router(assets.router,    prefix="/api/assets",     tags=["assets"])
app.include_router(catalogs.router,  prefix="/api/catalogs",   tags=["catalogs"])
app.include_router(persons.router,   prefix="/api/persons",    tags=["persons"])
app.include_router(reports.router,   prefix="/api/reports",    tags=["reports"])
app.include_router(evtx.router,      prefix="/api/evtx",       tags=["evtx"])
app.include_router(form_templates.router, prefix="/api/form-templates", tags=["양식 보고서"])
