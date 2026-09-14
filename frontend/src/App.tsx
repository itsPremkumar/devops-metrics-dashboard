"""DeployPulse main App component."""
import React, { useState, useEffect, useCallback } from 'react'
import { MetricsGrid } from './components/MetricsGrid'
import { DeploymentChart } from './components/Charts/DeploymentChart'
import { LeadTimeChart } from './components/Charts/LeadTimeChart'
import { FailureRateChart } from './components/Charts/FailureRateChart'
import { MTTRChart } from './components/Charts/MTTRChart'
import { PipelineTable } from './components/PipelineTable'
import { FilterBar } from './components/FilterBar'
import { useWebSocket } from './hooks/useWebSocket'
import { fetchDORAMetrics, fetchPipelineStatus } from './services/api'

export interface DORAMetrics {
  deployment_frequency: number
  lead_time_minutes: number
  change_failure_rate: number
  mttr_minutes: number
  period_days: number
  total_deployments: number
  successful_deployments: number
  failed_deployments: number
  team?: string
  project?: string
}

export interface PipelineRun {
  id: string
  name: string
  project: string
  team: string
  status: string
  stage: string
  started_at: string
  finished_at?: string
  source: string
}

function App() {
  const [metrics, setMetrics] = useState<DORAMetrics | null>(null)
  const [pipelines, setPipelines] = useState<PipelineRun[]>([])
  const [team, setTeam] = useState<string>('')
  const [project, setProject] = useState<string>('')
  const [days, setDays] = useState<number>(30)
  const [isLive, setIsLive] = useState(false)

  const loadMetrics = useCallback(async () => {
    try {
      const params = new URLSearchParams()
      if (team) params.set('team', team)
      if (project) params.set('project', project)
      params.set('days', days.toString())
      const data = await fetchDORAMetrics(params)
      setMetrics(data)
    } catch (err) {
      console.error('Failed to load metrics:', err)
    }
  }, [team, project, days])

  const loadPipelines = useCallback(async () => {
    try {
      const data = await fetchPipelineStatus()
      setPipelines(data.pipelines || [])
    } catch (err) {
      console.error('Failed to load pipelines:', err)
    }
  }, [])

  useEffect(() => {
    loadMetrics()
    loadPipelines()
    const interval = setInterval(loadPipelines, 30000)
    return () => clearInterval(interval)
  }, [loadMetrics, loadPipelines])

  const handleWebSocketMessage = useCallback((data: any) => {
    if (data.type === 'metrics_update') {
      setMetrics(data.data)
    }
  }, [])

  const wsUrl = `ws://${window.location.host}/ws`
  useWebSocket(wsUrl, handleWebSocketMessage, setIsLive)

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>DeployPulse</h1>
        <p className="version">v1.0.0 — DORA Dashboard</p>
        <nav>
          <div className="nav-item active">Dashboard</div>
          <div className="nav-item">Deployments</div>
          <div className="nav-item">Pipelines</div>
          <div className="nav-item">Reports</div>
          <div className="nav-item">Settings</div>
        </nav>
      </aside>
      <main className="main">
        <header className="header">
          <h2>DORA Metrics Overview</h2>
          <div className="live-indicator">
            <span className="live-dot"></span>
            {isLive ? 'Live' : 'Connecting...'}
          </div>
        </header>

        <FilterBar
          team={team}
          project={project}
          days={days}
          onTeamChange={setTeam}
          onProjectChange={setProject}
          onDaysChange={setDays}
        />

        <MetricsGrid metrics={metrics} />

        <div className="charts-grid">
          <DeploymentChart days={days} team={team} project={project} />
          <LeadTimeChart days={days} team={team} project={project} />
          <FailureRateChart days={days} team={team} project={project} />
          <MTTRChart days={days} team={team} project={project} />
        </div>

        <PipelineTable pipelines={pipelines} />
      </main>
    </div>
  )
}

export default App
