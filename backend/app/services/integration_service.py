"""Integration service — handles CI/CD platform connections."""
from datetime import datetime
from typing import Optional

from ..models import IntegrationStatus


class IntegrationService:
    def __init__(self):
        self._status = IntegrationStatus(
            github_actions=True,
            gitlab_ci=False,
            jenkins=False,
            last_sync=None,
        )
        self._github_token: Optional[str] = None
        self._gitlab_token: Optional[str] = None
        self._jenkins_url: Optional[str] = None

    def get_status(self) -> dict:
        return {
            "github_actions": {
                "connected": self._status.github_actions,
                "description": "GitHub Actions workflow monitoring",
                "webhook_configured": True,
            },
            "gitlab_ci": {
                "connected": self._status.gitlab_ci,
                "description": "GitLab CI/CD pipeline monitoring",
                "webhook_configured": False,
            },
            "jenkins": {
                "connected": self._status.jenkins,
                "description": "Jenkins build server monitoring",
                "webhook_configured": False,
            },
            "last_sync": self._status.last_sync.isoformat() if self._status.last_sync else None,
        }

    async def sync_github_actions(self) -> dict:
        """Simulate GitHub Actions sync."""
        self._status.github_actions = True
        self._status.last_sync = datetime.utcnow()
        return {
            "status": "ok",
            "message": "GitHub Actions sync completed",
            "workflows_synced": 12,
            "runs_synced": 248,
        }

    async def sync_gitlab_ci(self) -> dict:
        """Simulate GitLab CI sync."""
        self._status.gitlab_ci = True
        self._status.last_sync = datetime.utcnow()
        return {
            "status": "ok",
            "message": "GitLab CI sync completed",
            "pipelines_synced": 8,
        }

    async def sync_jenkins(self) -> dict:
        """Simulate Jenkins sync."""
        self._status.jenkins = True
        self._status.last_sync = datetime.utcnow()
        return {
            "status": "ok",
            "message": "Jenkins sync completed",
            "jobs_synced": 15,
        }

    def configure_github(self, token: str) -> dict:
        self._github_token = token
        self._status.github_actions = True
        return {"status": "ok", "message": "GitHub token configured"}

    def configure_gitlab(self, token: str, url: str = "https://gitlab.com") -> dict:
        self._gitlab_token = token
        self._status.gitlab_ci = True
        return {"status": "ok", "message": "GitLab token configured"}

    def configure_jenkins(self, url: str, username: str, token: str) -> dict:
        self._jenkins_url = url
        self._status.jenkins = True
        return {"status": "ok", "message": "Jenkins connection configured"}
