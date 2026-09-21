from fastapi import APIRouter
from app.modules.wait_fee.router import router as wait_fee_router
from app.routers import dashboard, fare, history, settings, tariff, trips

api = APIRouter(prefix="/api")
for r in (dashboard, trips, tariff, fare, history, settings):
    api.include_router(r.router)
api.include_router(wait_fee_router)
