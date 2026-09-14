"""Data models for DeployPulse metrics."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DeploymentRecord(BaseModel):
    id: str
    project: str
    team: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    commit_sha: Optional[str] = None
    branch: str = "main"
    environment: str = "production"
    duration_seconds: Optional[float] = None


class PipelineRun(BaseModel):
    id: str
    name: str
    project: str
    team: str
    status: str
    stage: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    source: str


class DORAMetrics(BaseModel):
    deployment_frequency: float
    lead_time_minutes: float
    change_failure_rate: float
    mttr_minutes: float
    period_days: int
    team: Optional[str] = None
    project: Optional[str] = None


class MetricsTimeSeries(BaseModel):
    date: str
    value: float


class PipelineStatus(BaseModel):
    total: int
    running: int
    success: int
    failed: int
    pipelines: List[PipelineRun]


class IntegrationStatus(BaseModel):
    github_actions: bool
    gitlab_ci: bool
    jenkins: bool
    last_sync: Optional[datetime] = None
