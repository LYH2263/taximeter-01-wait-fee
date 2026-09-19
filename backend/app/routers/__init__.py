from fastapi import APIRouter
from app.routers import dashboard, fare, history, settings, tariff, trips

api = APIRouter(prefix="/api")
for r in (dashboard, trips, tariff, fare, history, settings):
    api.include_router(r.router)
