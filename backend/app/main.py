from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.db.database import Base, engine, ensure_owner_column
from app.db import models
from app.routes.health import router as health_router
from app.routes.upload import router as upload_router
from app.routes.transactions import router as transactions_router
from app.routes.summary import router as summary_router
from app.routes.insights import router as insights_router
from app.routes.simulate import router as simulate_router
from app.routes.simulation_insights import router as simulation_insights_router

app = FastAPI(title="AI CFO Backend")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Test-User-Id"],
)

Base.metadata.create_all(bind=engine)
ensure_owner_column()

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(transactions_router)
app.include_router(summary_router)
app.include_router(insights_router)
app.include_router(simulate_router)
app.include_router(simulation_insights_router)


@app.get("/")
def root():
    return {"message": "AI CFO backend is running"}
