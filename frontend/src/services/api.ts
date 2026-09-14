const BASE_URL = import.meta.env.VITE_API_URL || ''

async function request<T>(path: string, params?: URLSearchParams): Promise<T> {
  const url = `${BASE_URL}${path}${params ? '?' + params.toString() : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export function fetchDORAMetrics(params?: URLSearchParams) {
  return request('/api/metrics/dora', params)
}

export function fetchDeploymentFrequency(params?: URLSearchParams) {
  return request('/api/metrics/deployments', params)
}

export function fetchLeadTime(params?: URLSearchParams) {
  return request('/api/metrics/lead-time', params)
}

export function fetchFailureRate(params?: URLSearchParams) {
  return request('/api/metrics/failure-rate', params)
}

export function fetchMTTR(params?: URLSearchParams) {
  return request('/api/metrics/mttr', params)
}

export function fetchPipelineStatus() {
  return request('/api/metrics/pipelines')
}

export function fetchTeams() {
  return request<string[]>('/api/filters/teams')
}

export function fetchProjects(team?: string) {
  const params = team ? new URLSearchParams({ team }) : undefined
  return request<string[]>('/api/filters/projects', params)
}

export function fetchIntegrationStatus() {
  return request('/api/integrations/status')
}
