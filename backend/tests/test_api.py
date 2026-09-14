"""DeployPulse pytest test suite."""
import pytest
from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


class TestHealth:
    def test_root(self):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json()["service"] == "DeployPulse"

    def test_health(self):
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"


class TestDORAMetrics:
    def test_dora_default(self):
        res = client.get("/api/metrics/dora")
        assert res.status_code == 200
        data = res.json()
        assert "deployment_frequency" in data
        assert "lead_time_minutes" in data
        assert "change_failure_rate" in data
        assert "mttr_minutes" in data

    def test_dora_with_team(self):
        res = client.get("/api/metrics/dora?team=platform")
        assert res.status_code == 200
        data = res.json()
        assert data["team"] == "platform"

    def test_dora_with_project(self):
        res = client.get("/api/metrics/dora?project=k8s-core&team=platform")
        assert res.status_code == 200
        data = res.json()
        assert data["project"] == "k8s-core"

    def test_dora_custom_days(self):
        res = client.get("/api/metrics/dora?days=7")
        assert res.status_code == 200
        assert res.json()["period_days"] == 7

    def test_deployments(self):
        res = client.get("/api/metrics/deployments")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_lead_time(self):
        res = client.get("/api/metrics/lead-time")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_failure_rate(self):
        res = client.get("/api/metrics/failure-rate")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_mttr(self):
        res = client.get("/api/metrics/mttr")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_pipeline_status(self):
        res = client.get("/api/metrics/pipelines")
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "running" in data
        assert "success" in data
        assert "failed" in data


class TestFilters:
    def test_teams(self):
        res = client.get("/api/filters/teams")
        assert res.status_code == 200
        teams = res.json()
        assert isinstance(teams, list)
        assert len(teams) > 0

    def test_projects(self):
        res = client.get("/api/filters/projects")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_projects_filtered(self):
        res = client.get("/api/filters/projects?team=frontend")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


class TestIntegrations:
    def test_status(self):
        res = client.get("/api/integrations/status")
        assert res.status_code == 200
        data = res.json()
        assert "github_actions" in data
        assert "gitlab_ci" in data
        assert "jenkins" in data

    def test_sync_github(self):
        res = client.post("/api/integrations/github-actions/sync")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_sync_gitlab(self):
        res = client.post("/api/integrations/gitlab-ci/sync")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_sync_jenkins(self):
        res = client.post("/api/integrations/jenkins/sync")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


class TestReports:
    def test_export_json(self):
        res = client.get("/api/reports/export?format=json")
        assert res.status_code == 200

    def test_export_csv(self):
        res = client.get("/api/reports/export?format=csv")
        assert res.status_code == 200


class TestWebSocket:
    def test_websocket_connection(self):
        with client.websocket_connect("/ws") as ws:
            data = ws.receive_json()
            assert data["type"] == "connected"

    def test_websocket_metrics(self):
        with client.websocket_connect("/ws") as ws:
            ws.receive_json()  # connected
            data = ws.receive_json()  # metrics
            assert data["type"] == "metrics"

    def test_websocket_filter(self):
        with client.websocket_connect("/ws") as ws:
            ws.receive_json()  # connected
            ws.receive_json()  # metrics
            ws.send_json({"action": "filter", "team": "platform", "days": 7})
            data = ws.receive_json()
            assert data["type"] == "metrics"
