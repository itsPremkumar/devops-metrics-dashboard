"""Failure Rate chart component."""
import React, { useEffect, useState } from 'react'
import { fetchFailureRate } from '../services/api'

interface Props {
  days: number
  team: string
  project: string
}

interface DataPoint {
  date: string
  failure_rate: number
  total: number
  failed: number
}

export function FailureRateChart({ days, team, project }: Props) {
  const [data, setData] = useState<DataPoint[]>([])

  useEffect(() => {
    const params = new URLSearchParams()
    if (team) params.set('team', team)
    if (project) params.set('project', project)
    params.set('days', days.toString())
    fetchFailureRate(params).then(setData).catch(console.error)
  }, [days, team, project])

  return (
    <div className="chart-card">
      <h3>Change Failure Rate (%)</h3>
      <div className="bar-chart failure">
        {data.slice(-14).map((point) => (
          <div key={point.date} className="bar-group">
            <div
              className="bar failure-bar"
              style={{ height: `${Math.min(point.failure_rate * 4, 100)}%` }}
              title={`${point.date}: ${point.failure_rate}%`}
            />
            <span className="bar-label">{point.date.slice(5)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
