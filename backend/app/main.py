from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.db import models
from app.routes.health import router as health_router
from app.routes.upload import router as upload_router
from app.routes.transactions import router as transactions_router
from app.routes.summary import router as summary_router
from app.routes.insights import router as insights_router
from app.routes.simulate import router as simulate_router
from app.routes.simulation_insights import router as simulation_insights_router

app = FastAPI(title="AI CFO Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

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