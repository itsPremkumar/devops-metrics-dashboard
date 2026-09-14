# DeployPulse

DeployPulse is a DevOps Metrics & DORA Dashboard that provides real-time insights into your CI/CD pipeline health, deployment frequency, lead time for changes, change failure rate, and mean time to recovery.

## Features

- 4 DORA metrics: Deployment Frequency, Lead Time, Change Failure Rate, MTTR
- Real-time updates via WebSockets
- Team and project-level filtering
- Integration with GitHub Actions, GitLab CI, and Jenkins
- Exportable reports (PDF, CSV, JSON)
- Pipeline status monitoring
- Responsive React dashboard

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

API available at http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard at http://localhost:3000

### Docker Compose

```bash
docker-compose up --build
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/metrics/dora` | GET | DORA metrics summary |
| `/api/metrics/deployments` | GET | Deployment frequency series |
| `/api/metrics/lead-time` | GET | Lead time for changes series |
| `/api/metrics/failure-rate` | GET | Change failure rate series |
| `/api/metrics/mttr` | GET | MTTR series |
| `/api/metrics/pipelines` | GET | Pipeline status summary |
| `/api/integrations/status` | GET | Integration connectivity |
| `/api/integrations/github-actions/sync` | POST | Sync GitHub Actions |
| `/api/integrations/gitlab-ci/sync` | POST | Sync GitLab CI |
| `/api/integrations/jenkins/sync` | POST | Sync Jenkins |
| `/api/reports/export` | GET | Export report (pdf/csv/json) |
| `/ws` | WebSocket | Real-time metrics stream |

## Integrations

### GitHub Actions

Add to your workflow YAML:
```yaml
- name: Send DeployPulse event
  run: |
    curl -X POST https://your-deploypulse/api/webhook/github \
      -H "Authorization: Bearer ${{ secrets.DEPLOYPULSE_TOKEN }}" \
      -d '{"repository":"${{ github.repository }}","status":"${{ job.status }}","sha":"${{ github.sha }}"}'
```

### GitLab CI

Add to your `.gitlab-ci.yml`:
```yaml
notify:
  script:
    - 'curl -X POST https://your-deploypulse/api/webhook/gitlab -H "Authorization: Bearer $DEPLOYPULSE_TOKEN" -d "{\"project\":\"$CI_PROJECT_NAME\",\"status\":\"$CI_JOB_STATUS\",\"pipeline_id\":\"$CI_PIPELINE_ID\"}"'
```

### Jenkins

Add a post-build step:
```groovy
post {
  always {
    sh 'curl -X POST https://your-deploypulse/api/webhook/jenkins -H "Authorization: Bearer $DEPLOYPULSE_TOKEN" -d "{\"job\":\"$JOB_NAME\",\"status\":\"$BUILD_STATUS\",\"number\":\"$BUILD_NUMBER\"}"'
  }
}
```

## DORA Metrics Explained

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| Deployment Frequency | Multiple/day | 1/day - 1/week | 1/week - 1/month | < 1/month |
| Lead Time | < 1 hour | 1 hour - 1 day | 1 day - 1 week | > 1 week |
| Change Failure Rate | 0-15% | 0-15% | 0-15% | > 45% |
| MTTR | < 1 hour | < 1 day | 1 day - 1 week | > 1 week |

## Screenshots

![Dashboard](docs/screenshots/dashboard.png)
*DeployPulse DORA Dashboard showing deployment frequency, lead time, failure rate, and MTTR charts*

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Pydantic v2, Uvicorn
- **Frontend:** React 18, TypeScript, Vite, CSS3
- **Real-time:** WebSocket (native FastAPI)
- **CI/CD:** GitHub Actions
- **Deployment:** Docker, Docker Compose

## License

MIT
