from fastapi import APIRouter
from app.routers import dashboard, fare, history, settings, tariff, trips, wait_fee

api = APIRouter(prefix="/api")
for r in (dashboard, trips, tariff, wait_fee, fare, history, settings):
    api.include_router(r.router)
