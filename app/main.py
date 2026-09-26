from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.patients import router as patients_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Voice AI Patient Registration API",
    description="REST API backing a voice-based patient intake agent.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(patients_router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "patient-registration-api"}