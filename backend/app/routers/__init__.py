"""API routers for DeployPulse."""
from fastapi import APIRouter

from ..services.metrics_service import MetricsService

router = APIRouter()
metrics_service = MetricsService()


@router.get("/summary")
async def summary():
    return metrics_service.get_dora_metrics()


@router.get("/deployments/recent")
async def recent_deployments(limit: int = 20):
    return metrics_service._deployments[:limit]
