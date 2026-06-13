from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    from config import get_settings
    app.state.settings = get_settings()
    yield


app = FastAPI(
    title="ProspecMan API",
    version="1.0.0",
    description="Converta briefing de audio em estrutura de projeto completa com IA.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
