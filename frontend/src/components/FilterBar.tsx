"""Filter bar component — team, project, and time range filters."""
import React, { useEffect, useState } from 'react'
import { fetchTeams, fetchProjects } from '../services/api'

interface Props {
  team: string
  project: string
  days: number
  onTeamChange: (team: string) => void
  onProjectChange: (project: string) => void
  onDaysChange: (days: number) => void
}

export function FilterBar({ team, project, days, onTeamChange, onProjectChange, onDaysChange }: Props) {
  const [teams, setTeams] = useState<string[]>([])
  const [projects, setProjects] = useState<string[]>([])

  useEffect(() => {
    fetchTeams().then(setTeams).catch(console.error)
  }, [])

  useEffect(() => {
    fetchProjects(team).then(setProjects).catch(console.error)
  }, [team])

  return (
    <div className="filters">
      <select
        className="filter-select"
        value={team}
        onChange={(e) => onTeamChange(e.target.value)}
      >
        <option value="">All Teams</option>
        {teams.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
      <select
        className="filter-select"
        value={project}
        onChange={(e) => onProjectChange(e.target.value)}
      >
        <option value="">All Projects</option>
        {projects.map((p) => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>
      <select
        className="filter-select"
        value={days}
        onChange={(e) => onDaysChange(Number(e.target.value))}
      >
        <option value={7}>Last 7 days</option>
        <option value={14}>Last 14 days</option>
        <option value={30}>Last 30 days</option>
        <option value={60}>Last 60 days</option>
        <option value={90}>Last 90 days</option>
      </select>
    </div>
  )
}
