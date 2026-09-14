"""Pipeline table component — displays recent pipeline runs."""
import React from 'react'
import { PipelineRun } from '../App'

interface Props {
  pipelines: PipelineRun[]
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const diff = Math.floor((now.getTime() - d.getTime()) / 60000)
  if (diff < 1) return 'just now'
  if (diff < 60) return `${diff}m ago`
  if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
  return d.toLocaleDateString()
}

function sourceBadge(source: string): string {
  switch (source) {
    case 'github_actions': return 'GH Actions'
    case 'gitlab_ci': return 'GitLab CI'
    case 'jenkins': return 'Jenkins'
    default: return source
  }
}

export function PipelineTable({ pipelines }: Props) {
  return (
    <div className="pipeline-list">
      <h3>Recent Pipelines</h3>
      {pipelines.map((p) => (
        <div key={p.id} className="pipeline-item">
          <span className={`status-dot ${p.status}`} />
          <div className="pipeline-name">
            <div>{p.name}</div>
            <div className="pipeline-meta">
              {p.project} &middot; {sourceBadge(p.source)} &middot; {p.stage}
            </div>
          </div>
          <span className="pipeline-time">{formatTime(p.started_at)}</span>
        </div>
      ))}
      {pipelines.length === 0 && (
        <div className="empty-state">No recent pipelines</div>
      )}
    </div>
  )
}
