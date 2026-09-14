"""Metrics service — generates and serves DORA metrics with sample data."""
import random
import math
from datetime import datetime, timedelta
from typing import List, Optional

from ..models import (
    DeploymentRecord,
    PipelineRun,
    DORAMetrics,
    MetricsTimeSeries,
    PipelineStatus,
)


class MetricsService:
    def __init__(self):
        self._start_time = datetime.utcnow()
        self._deployments = self._generate_deployments()
        self._pipelines = self._generate_pipelines()

    def uptime_seconds(self) -> float:
        return (datetime.utcnow() - self._start_time).total_seconds()

    def _generate_deployments(self) -> List[DeploymentRecord]:
        """Generate realistic sample deployment data for the last 90 days."""
        teams = ["platform", "frontend", "backend", "data", "mobile"]
        projects = {
            "platform": ["k8s-core", "infra-monitoring", "service-mesh"],
            "frontend": ["web-app", "design-system", "admin-panel"],
            "backend": ["api-gateway", "auth-service", "payment-svc"],
            "data": ["etl-pipeline", "ml-platform", "analytics"],
            "mobile": ["ios-app", "android-app", "react-native"],
        }
        environments = ["staging", "production"]
        deployments = []
        now = datetime.utcnow()

        for day_offset in range(90):
            date = now - timedelta(days=day_offset)
            # 1-5 deployments per day
            num_deployments = random.randint(1, 5)
            for _ in range(num_deployments):
                team = random.choice(teams)
                project = random.choice(projects[team])
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                started = date.replace(hour=hour, minute=minute, second=0)
                duration = random.uniform(60, 1800)  # 1-30 min
                completed = started + timedelta(seconds=duration)
                status = random.choices(
                    ["success", "failed", "in_progress"],
                    weights=[0.85, 0.10, 0.05],
                )[0]

                deployments.append(
                    DeploymentRecord(
                        id=f"dep-{len(deployments)+1:04d}",
                        project=project,
                        team=team,
                        status=status,
                        started_at=started,
                        completed_at=completed if status != "in_progress" else None,
                        commit_sha=f"{random.getrandbits(160):040x}"[:8],
                        branch=random.choice(["main", "release", "hotfix"]),
                        environment=random.choice(environments),
                        duration_seconds=duration,
                    )
                )
        return sorted(deployments, key=lambda d: d.started_at, reverse=True)

    def _generate_pipelines(self) -> List[PipelineRun]:
        """Generate current pipeline statuses."""
        sources = ["github_actions", "gitlab_ci", "jenkins"]
        pipelines = []
        for i in range(20):
            team = random.choice(["platform", "frontend", "backend", "data", "mobile"])
            source = random.choice(sources)
            status = random.choices(
                ["success", "failed", "running", "pending"],
                weights=[0.6, 0.15, 0.15, 0.10],
            )[0]
            started = datetime.utcnow() - timedelta(minutes=random.randint(1, 120))
            finished = None
            if status in ("success", "failed"):
                finished = started + timedelta(minutes=random.randint(2, 30))

            pipelines.append(
                PipelineRun(
                    id=f"pipe-{i+1:04d}",
                    name=f"ci-{team}-{random.randint(1,5)}",
                    project=f"{team}-project",
                    team=team,
                    status=status,
                    stage=random.choice(["build", "test", "deploy", "verify"]),
                    started_at=started,
                    finished_at=finished,
                    source=source,
                )
            )
        return pipelines

    def get_dora_metrics(
        self,
        team: Optional[str] = None,
        project: Optional[str] = None,
        days: int = 30,
    ) -> dict:
        """Calculate DORA metrics for the given filters."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deps = self._filter_deployments(team, project, cutoff)

        if not deps:
            return {
                "deployment_frequency": 0.0,
                "lead_time_minutes": 0.0,
                "change_failure_rate": 0.0,
                "mttr_minutes": 0.0,
                "period_days": days,
                "total_deployments": 0,
                "team": team,
                "project": project,
            }

        # Deployment frequency: deployments per day
        total = len(deps)
        freq = total / days

        # Lead time: median duration of successful deployments
        successful = [d for d in deps if d.status == "success" and d.duration_seconds]
        lead_times = [d.duration_seconds / 60 for d in successful] if successful else [0]
        lead_times.sort()
        median_lead = lead_times[len(lead_times) // 2]

        # Change failure rate
        completed = [d for d in deps if d.status in ("success", "failed")]
        failed = [d for d in completed if d.status == "failed"]
        failure_rate = (len(failed) / len(completed) * 100) if completed else 0.0

        # MTTR: average time from failure detection to recovery
        # Simulated: average time between a failed deploy and next successful one
        mttr = random.uniform(15, 120) if failed else 0.0

        return {
            "deployment_frequency": round(freq, 2),
            "lead_time_minutes": round(median_lead, 1),
            "change_failure_rate": round(failure_rate, 1),
            "mttr_minutes": round(mttr, 1),
            "period_days": days,
            "total_deployments": total,
            "successful_deployments": len(successful),
            "failed_deployments": len(failed),
            "team": team,
            "project": project,
        }

    def get_deployment_frequency(
        self,
        team: Optional[str] = None,
        project: Optional[str] = None,
        days: int = 30,
    ) -> List[dict]:
        """Daily deployment frequency time series."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deps = self._filter_deployments(team, project, cutoff)
        series = {}
        for d in deps:
            day = d.started_at.strftime("%Y-%m-%d")
            series[day] = series.get(day, 0) + 1

        return [{"date": k, "deployments": v} for k, v in sorted(series.items())]

    def get_lead_time(
        self,
        team: Optional[str] = None,
        project: Optional[str] = None,
        days: int = 30,
    ) -> List[dict]:
        """Lead time for changes time series (minutes)."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deps = self._filter_deployments(team, project, cutoff)
        series = {}
        for d in deps:
            if d.status == "success" and d.duration_seconds:
                day = d.started_at.strftime("%Y-%m-%d")
                if day not in series:
                    series[day] = []
                series[day].append(d.duration_seconds / 60)

        result = []
        for day in sorted(series.keys()):
            times = series[day]
            result.append({
                "date": day,
                "median_minutes": round(sorted(times)[len(times) // 2], 1),
                "p95_minutes": round(sorted(times)[int(len(times) * 0.95)], 1),
                "avg_minutes": round(sum(times) / len(times), 1),
            })
        return result

    def get_failure_rate(
        self,
        team: Optional[str] = None,
        project: Optional[str] = None,
        days: int = 30,
    ) -> List[dict]:
        """Daily failure rate percentage."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deps = self._filter_deployments(team, project, cutoff)
        series = {}
        for d in deps:
            day = d.started_at.strftime("%Y-%m-%d")
            if day not in series:
                series[day] = {"total": 0, "failed": 0}
            series[day]["total"] += 1
            if d.status == "failed":
                series[day]["failed"] += 1

        return [
            {
                "date": day,
                "failure_rate": round(s["failed"] / s["total"] * 100, 1),
                "total": s["total"],
                "failed": s["failed"],
            }
            for day, s in sorted(series.items())
        ]

    def get_mttr(
        self,
        team: Optional[str] = None,
        project: Optional[str] = None,
        days: int = 30,
    ) -> List[dict]:
        """MTTR time series (minutes)."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        deps = self._filter_deployments(team, project, cutoff)
        series = {}
        for d in deps:
            if d.status == "failed":
                day = d.started_at.strftime("%Y-%m-%d")
                # Simulated recovery time
                recovery = random.uniform(10, 180)
                if day not in series:
                    series[day] = []
                series[day].append(recovery)

        return [
            {"date": day, "mttr_minutes": round(sum(times) / len(times), 1)}
            for day, times in sorted(series.items())
        ]

    def get_pipeline_status(self) -> dict:
        """Current pipeline status summary."""
        running = [p for p in self._pipelines if p.status == "running"]
        success = [p for p in self._pipelines if p.status == "success"]
        failed = [p for p in self._pipelines if p.status == "failed"]
        pending = [p for p in self._pipelines if p.status == "pending"]

        return {
            "total": len(self._pipelines),
            "running": len(running),
            "success": len(success),
            "failed": len(failed),
            "pending": len(pending),
            "pipelines": [p.dict() for p in self._pipelines[:10]],
        }

    def get_teams(self) -> List[str]:
        return sorted(set(d.team for d in self._deployments))

    def get_projects(self, team: Optional[str] = None) -> List[str]:
        deps = self._deployments
        if team:
            deps = [d for d in deps if d.team == team]
        return sorted(set(d.project for d in deps))

    def _filter_deployments(
        self,
        team: Optional[str],
        project: Optional[str],
        cutoff: datetime,
    ) -> List[DeploymentRecord]:
        result = [d for d in self._deployments if d.started_at >= cutoff]
        if team:
            result = [d for d in result if d.team == team]
        if project:
            result = [d for d in result if d.project == project]
        return result
