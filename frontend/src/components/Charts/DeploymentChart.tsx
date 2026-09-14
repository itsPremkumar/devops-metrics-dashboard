"""Deployment Frequency chart component."""
import React, { useEffect, useState } from 'react'
import { fetchDeploymentFrequency } from '../services/api'

interface Props {
  days: number
  team: string
  project: string
}

interface DataPoint {
  date: string
  deployments: number
}

export function DeploymentChart({ days, team, project }: Props) {
  const [data, setData] = useState<DataPoint[]>([])

  useEffect(() => {
    const params = new URLSearchParams()
    if (team) params.set('team', team)
    if (project) params.set('project', project)
    params.set('days', days.toString())
    fetchDeploymentFrequency(params).then(setData).catch(console.error)
  }, [days, team, project])

  const max = Math.max(...data.map((d) => d.deployments), 1)

  return (
    <div className="chart-card">
      <h3>Deployment Frequency (per day)</h3>
      <div className="bar-chart">
        {data.slice(-14).map((point) => (
          <div key={point.date} className="bar-group">
            <div
              className="bar"
              style={{ height: `${(point.deployments / max) * 100}%` }}
              title={`${point.date}: ${point.deployments} deployments`}
            />
            <span className="bar-label">{point.date.slice(5)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
