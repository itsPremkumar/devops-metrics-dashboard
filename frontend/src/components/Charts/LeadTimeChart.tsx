"""Lead Time chart component."""
import React, { useEffect, useState } from 'react'
import { fetchLeadTime } from '../services/api'

interface Props {
  days: number
  team: string
  project: string
}

interface DataPoint {
  date: string
  median_minutes: number
  p95_minutes: number
  avg_minutes: number
}

export function LeadTimeChart({ days, team, project }: Props) {
  const [data, setData] = useState<DataPoint[]>([])

  useEffect(() => {
    const params = new URLSearchParams()
    if (team) params.set('team', team)
    if (project) params.set('project', project)
    params.set('days', days.toString())
    fetchLeadTime(params).then(setData).catch(console.error)
  }, [days, team, project])

  const max = Math.max(...data.map((d) => d.p95_minutes), 1)

  return (
    <div className="chart-card">
      <h3>Lead Time for Changes (minutes)</h3>
      <div className="line-chart">
        {data.slice(-14).map((point) => (
          <div key={point.date} className="line-point">
            <div
              className="line-bar median"
              style={{ height: `${(point.median_minutes / max) * 100}%` }}
              title={`Median: ${point.median_minutes} min`}
            />
            <div
              className="line-bar p95"
              style={{ height: `${(point.p95_minutes / max) * 100}%` }}
              title={`P95: ${point.p95_minutes} min`}
            />
            <span className="line-label">{point.date.slice(5)}</span>
          </div>
        ))}
      </div>
      <div className="legend">
        <span className="legend-item"><span className="dot median" /> Median</span>
        <span className="legend-item"><span className="dot p95" /> P95</span>
      </div>
    </div>
  )
}
