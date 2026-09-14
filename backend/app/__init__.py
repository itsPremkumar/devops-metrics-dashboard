"""
DeployPulse - DevOps Metrics & DORA Dashboard
FastAPI backend with WebSocket support, CI/CD integrations, and report generation.
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from .connections import ConnectionManager
from .services.metrics_service import MetricsService
from .services.report_service import ReportService
from .services.integration_service import IntegrationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deploypulse")

app = FastAPI(
    title="DeployPulse",
    description="DevOps Metrics & DORA Dashboard Backend",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
metrics_service = MetricsService()
integration_service = IntegrationService()
report_service = ReportService()
manager = ConnectionManager()


@app.get("/")
async def root():
    return {"status": "ok", "service": "DeployPulse", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": metrics_service.uptime_seconds(),
    }


# ---- DORA Metrics ----

@app.get("/api/metrics/dora")
async def dora_metrics(
    team: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    return metrics_service.get_dora_metrics(team=team, project=project, days=days)


@app.get("/api/metrics/deployments")
async def deployment_metrics(
    team: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    return metrics_service.get_deployment_frequency(team=team, project=project, days=days)


@app.get("/api/metrics/lead-time")
async def lead_time_metrics(
    team: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    return metrics_service.get_lead_time(team=team, project=project, days=days)


@app.get("/api/metrics/failure-rate")
async def failure_rate_metrics(
    team: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    return metrics_service.get_failure_rate(team=team, project=project, days=days)


@app.get("/api/metrics/mttr")
async def mttr_metrics(
    team: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    return metrics_service.get_mttr(team=team, project=project, days=days)


@app.get("/api/metrics/pipelines")
async def pipeline_status():
    return metrics_service.get_pipeline_status()


# ---- Integrations ----

@app.get("/api/integrations/status")
async def integration_status():
    return integration_service.get_status()


@app.post("/api/integrations/github-actions/sync")
async def sync_github_actions():
    return await integration_service.sync_github_actions()


@app.post("/api/integrations/gitlab-ci/sync")
async def sync_gitlab_ci():
    return await integration_service.sync_gitlab_ci()


@app.post("/api/integrations/jenkins/sync")
async def sync_jenkins():
    return await integration_service.sync_jenkins()


# ---- Filters ----

@app.get("/api/filters/teams")
async def list_teams():
    return metrics_service.get_teams()


@app.get("/api/filters/projects")
async def list_projects(team: Optional[str] = Query(None)):
    return metrics_service.get_projects(team=team)


# ---- Reports ----

@app.get("/api/reports/export")
async def export_report(
    format: str = Query("pdf", regex="^(pdf|csv|json)$"),
    team: Optional[str] = Query(None),
    project: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
):
    file_path = await report_service.generate(
        format=format, team=team, project=project, days=days
    )
    return FileResponse(
        file_path,
        filename=f"deploypulse_report.{format}",
        media_type="application/octet-stream",
    )


# ---- WebSocket ----

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial data
        await websocket.send_json({
            "type": "connected",
            "data": {"message": "DeployPulse real-time feed connected"},
        })
        # Send current metrics
        await websocket.send_json({
            "type": "metrics",
            "data": metrics_service.get_dora_metrics(),
        })

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "filter":
                    filtered = metrics_service.get_dora_metrics(
                        team=msg.get("team"),
                        project=msg.get("project"),
                        days=msg.get("days", 30),
                    )
                    await websocket.send_json({
                        "type": "metrics",
                        "data": filtered,
                    })
                elif msg.get("action") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"},
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Background task to broadcast updates
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_loop())


async def broadcast_loop():
    """Broadcast real-time metrics updates every 30 seconds."""
    while True:
        await asyncio.sleep(30)
        data = {
            "type": "metrics_update",
            "data": metrics_service.get_dora_metrics(),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await manager.broadcast(data)


from . import models, routers  # noqa
