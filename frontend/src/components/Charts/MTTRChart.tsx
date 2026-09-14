"""MTTR chart component."""
import React, { useEffect, useState } from 'react'
import { fetchMTTR } from '../services/api'

interface Props {
  days: number
  team: string
  project: string
}

interface DataPoint {
  date: string
  mttr_minutes: number
}

export function MTTRChart({ days, team, project }: Props) {
  const [data, setData] = useState<DataPoint[]>([])

  useEffect(() => {
    const params = new URLSearchParams()
    if (team) params.set('team', team)
    if (project) params.set('project', project)
    params.set('days', days.toString())
    fetchMTTR(params).then(setData).catch(console.error)
  }, [days, team, project])

  const max = Math.max(...data.map((d) => d.mttr_minutes), 1)

  return (
    <div className="chart-card">
      <h3>Mean Time to Recovery (minutes)</h3>
      <div className="bar-chart mttr">
        {data.slice(-14).map((point) => (
          <div key={point.date} className="bar-group">
            <div
              className="bar mttr-bar"
              style={{ height: `${(point.mttr_minutes / max) * 100}%` }}
              title={`${point.date}: ${point.mttr_minutes} min`}
            />
            <span className="bar-label">{point.date.slice(5)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
