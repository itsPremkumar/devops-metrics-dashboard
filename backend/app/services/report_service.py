"""Report service — generates exportable reports (PDF, CSV, JSON)."""
import asyncio
import csv
import io
import json
import os
from datetime import datetime
from typing import Optional

from .metrics_service import MetricsService


class ReportService:
    def __init__(self):
        self.metrics_service = MetricsService()
        self.reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    async def generate(
        self,
        format: str,
        team: Optional[str],
        project: Optional[str],
        days: int,
    ) -> str:
        """Generate report file and return path."""
        metrics = self.metrics_service.get_dora_metrics(team, project, days)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"deploypulse_{team or 'all'}_{project or 'all'}_{timestamp}.{format}"
        path = os.path.join(self.reports_dir, filename)

        if format == "json":
            await self._generate_json(path, metrics)
        elif format == "csv":
            await self._generate_csv(path, metrics)
        elif format == "pdf":
            await self._generate_pdf(path, metrics)

        return path

    async def _generate_json(self, path: str, metrics: dict):
        import aiofiles
        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(metrics, indent=2, default=str))

    async def _generate_csv(self, path: str, metrics: dict):
        import aiofiles
        async with aiofiles.open(path, "w", newline="") as f:
            writer = csv.writer(f)
            await f.write("Metric,Value\n")
            for key, value in metrics.items():
                await f.write(f"{key},{value}\n")

            # Add time series data
            await f.write("\n\nDeployment Frequency\n")
            await f.write("Date,Deployments\n")
            for point in self.metrics_service.get_deployment_frequency(days=metrics["period_days"]):
                await f.write(f"{point['date']},{point['deployments']}\n")

            await f.write("\nLead Time\n")
            await f.write("Date,Median Minutes,P95 Minutes,Avg Minutes\n")
            for point in self.metrics_service.get_lead_time(days=metrics["period_days"]):
                await f.write(
                    f"{point['date']},{point['median_minutes']},"
                    f"{point['p95_minutes']},{point['avg_minutes']}\n"
                )

            await f.write("\nFailure Rate\n")
            await f.write("Date,Failure Rate %,Total,Failed\n")
            for point in self.metrics_service.get_failure_rate(days=metrics["period_days"]):
                await f.write(
                    f"{point['date']},{point['failure_rate']},"
                    f"{point['total']},{point['failed']}\n"
                )

    async def _generate_pdf(self, path: str, metrics: dict):
        """Generate a text-based PDF report (simplified)."""
        import aiofiles
        async with aiofiles.open(path, "w") as f:
            await f.write("DEPLOYPULSE - DevOps Metrics Report\n")
            await f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            await f.write(f"Period: {metrics['period_days']} days\n")
            if metrics.get("team"):
                await f.write(f"Team: {metrics['team']}\n")
            if metrics.get("project"):
                await f.write(f"Project: {metrics['project']}\n")
            await f.write("\n--- DORA METRICS ---\n")
            await f.write(f"Deployment Frequency: {metrics['deployment_frequency']}/day\n")
            await f.write(f"Lead Time for Changes: {metrics['lead_time_minutes']} min\n")
            await f.write(f"Change Failure Rate: {metrics['change_failure_rate']}%\n")
            await f.write(f"MTTR: {metrics['mttr_minutes']} min\n")
            await f.write(f"\nTotal Deployments: {metrics['total_deployments']}\n")
            await f.write(f"Successful: {metrics['successful_deployments']}\n")
            await f.write(f"Failed: {metrics['failed_deployments']}\n")
