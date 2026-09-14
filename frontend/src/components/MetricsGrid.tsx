"""Metrics Grid component — displays DORA metric cards."""
import React from 'react'
import { DORAMetrics } from '../App'

interface Props {
  metrics: DORAMetrics | null
}

export function MetricsGrid({ metrics }: Props) {
  if (!metrics) {
    return <div className="metrics-grid loading">Loading metrics...</div>
  }

  const cards = [
    {
      label: 'Deployment Frequency',
      value: metrics.deployment_frequency,
      unit: '/day',
      trend: 'up',
      trendText: '+12% vs last period',
    },
    {
      label: 'Lead Time for Changes',
      value: metrics.lead_time_minutes,
      unit: 'min',
      trend: 'down',
      trendText: '-8% vs last period',
    },
    {
      label: 'Change Failure Rate',
      value: metrics.change_failure_rate,
      unit: '%',
      trend: 'down',
      trendText: '-3% vs last period',
    },
    {
      label: 'MTTR',
      value: metrics.mttr_minutes,
      unit: 'min',
      trend: 'down',
      trendText: '-15% vs last period',
    },
  ]

  return (
    <div className="metrics-grid">
      {cards.map((card) => (
        <div key={card.label} className="metric-card">
          <div className="label">{card.label}</div>
          <div className="value">
            {card.value}
            <span className="unit">{card.unit}</span>
          </div>
          <div className={`trend ${card.trend}`}>{card.trendText}</div>
        </div>
      ))}
    </div>
  )
}
