from fastapi import APIRouter, Request
from backend.app.core.limiter import limiter

from backend.app.services.dashboard_service import dashboard_stats
from backend.app.services.training_service import load_metrics

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/stats")
@limiter.limit("30/minute")
def stats(request: Request):
    return dashboard_stats()


@router.get("/metrics")
@limiter.limit("30/minute")
async def metrics(request: Request):
    return load_metrics()


@router.get("/equipment/{equipment_id}")
@limiter.limit("60/minute")
async def equipment(request: Request, equipment_id: str):
    return {
        "equipment_id": equipment_id,
        "type": "camion-benne" if "truck" in equipment_id.lower() else "équipement minier",
        "status": "surveillance",
        "last_seen": "temps réel simulé",
        "maintenance_policy": "inspection conditionnelle basée sur risque IA",
    }