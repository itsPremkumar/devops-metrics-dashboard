var BASE_URL = window.__DEPLOYPULSE_API_URL__ || ''

function request(path, params) {
  var qs = params && params.toString() ? '?' + params.toString() : ''
  var url = BASE_URL + path + qs
  return fetch(url).then(function(res) {
    if (!res.ok) throw new Error('API error: ' + res.status)
    return res.json()
  })
}

module.exports = {
  fetchDORAMetrics: function(params) { return request('/api/metrics/dora', params) },
  fetchDeploymentFrequency: function(params) { return request('/api/metrics/deployments', params) },
  fetchLeadTime: function(params) { return request('/api/metrics/lead-time', params) },
  fetchFailureRate: function(params) { return request('/api/metrics/failure-rate', params) },
  fetchMTTR: function(params) { return request('/api/metrics/mttr', params) },
  fetchPipelineStatus: function() { return request('/api/metrics/pipelines') },
  fetchTeams: function() { return request('/api/filters/teams') },
  fetchProjects: function(team) {
    var params = team ? new URLSearchParams({ team: team }) : undefined
    return request('/api/filters/projects', params)
  },
  fetchIntegrationStatus: function() { return request('/api/integrations/status') },
}
