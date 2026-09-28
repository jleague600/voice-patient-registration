from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes.patients import router as patients_router
from app.db.init_db import init_db


# This runs when the app starts. It creates the database tables first.
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


# This is the main app. All API routes are attached here.
app = FastAPI(
    title="Voice AI Patient Registration API",
    description="REST API backing a voice-based patient intake agent.",
    version="1.0.0",
    lifespan=lifespan,
)

# Add the patient API routes to the app.
app.include_router(patients_router)


# Small health check route. Useful to see if the app is alive.
@app.get("/")
async def root():
    return {"status": "ok", "service": "patient-registration-api"}