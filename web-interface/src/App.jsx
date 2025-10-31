import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function App() {
  const [servers, setServers] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Fetch all data
  const fetchData = async () => {
    try {
      const [serversRes, metricsRes, healthRes] = await Promise.all([
        axios.get(`${API_BASE}/api/servers`),
        axios.get(`${API_BASE}/api/metrics`),
        axios.get(`${API_BASE}/api/health`)
      ])

      setServers(serversRes.data.servers || [])
      setMetrics(metricsRes.data)
      setHealth(healthRes.data)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Auto-refresh every 5 seconds
  useEffect(() => {
    fetchData()
    
    if (autoRefresh) {
      const interval = setInterval(fetchData, 5000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  // Run load test
  const runLoadTest = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/load-test`, {
        target_servers: servers.slice(0, 10).map(s => s.id),
        requests: 100,
        concurrency: 10
      })
      alert('Load test completed! Check console for results.')
      console.log('Load test results:', response.data)
      fetchData()
    } catch (err) {
      alert('Load test failed: ' + err.message)
    }
  }

  // Simulate load on servers
  const simulateLoad = async () => {
    try {
      await axios.post(`${API_BASE}/api/simulate-load`, {
        server_ids: [1, 2, 3, 4, 5],
        cpu_duration: 3.0,
        memory_mb: 100
      })
      alert('Load simulation started on first 5 servers')
      setTimeout(fetchData, 3000)
    } catch (err) {
      alert('Load simulation failed: ' + err.message)
    }
  }

  // Broadcast request
  const broadcastRequest = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/broadcast?endpoint=/`)
      alert(`Broadcast complete! ${response.data.successful_responses}/${response.data.total_servers} responded`)
    } catch (err) {
      alert('Broadcast failed: ' + err.message)
    }
  }

  if (loading) {
    return <div className="loading">Loading Server Farm</div>
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>Error connecting to Control Plane</h2>
          <p>{error}</p>
          <p>Make sure the control plane is running at {API_BASE}</p>
          <button className="btn btn-primary" onClick={fetchData}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  const runningServers = servers.filter(s => s.status === 'running').length
  const healthyServers = health?.healthy || 0
  const degradedServers = health?.degraded || 0

  return (
    <div className="app">
      <header className="header">
        <h1>🖥️ Server Farm Control Panel</h1>
        <p>Managing {servers.length} Virtual Servers</p>
      </header>

      <div className="controls">
        <button className="btn btn-primary" onClick={fetchData}>
          🔄 Refresh Now
        </button>
        <button 
          className={`btn ${autoRefresh ? 'btn-success' : 'btn-secondary'}`}
          onClick={() => setAutoRefresh(!autoRefresh)}
        >
          {autoRefresh ? '⏸️ Pause Auto-Refresh' : '▶️ Start Auto-Refresh'}
        </button>
        <button className="btn btn-warning" onClick={runLoadTest}>
          ⚡ Run Load Test
        </button>
        <button className="btn btn-primary" onClick={simulateLoad}>
          💪 Simulate Load
        </button>
        <button className="btn btn-success" onClick={broadcastRequest}>
          📡 Broadcast Request
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Servers</h3>
          <div className="value">{servers.length}</div>
          <div className="subtext">Configured instances</div>
        </div>
        
        <div className="stat-card">
          <h3>Running</h3>
          <div className="value" style={{ color: 'var(--accent-success)' }}>
            {runningServers}
          </div>
          <div className="subtext">{((runningServers / servers.length) * 100).toFixed(1)}% uptime</div>
        </div>
        
        <div className="stat-card">
          <h3>Healthy</h3>
          <div className="value" style={{ color: 'var(--accent-success)' }}>
            {healthyServers}
          </div>
          <div className="subtext">Passing health checks</div>
        </div>
        
        <div className="stat-card">
          <h3>Degraded</h3>
          <div className="value" style={{ color: 'var(--accent-warning)' }}>
            {degradedServers}
          </div>
          <div className="subtext">Performance issues</div>
        </div>

        {metrics?.aggregated_metrics && (
          <>
            <div className="stat-card">
              <h3>Avg CPU Usage</h3>
              <div className="value">
                {metrics.aggregated_metrics.cpu.average.toFixed(1)}%
              </div>
              <div className="subtext">
                Max: {metrics.aggregated_metrics.cpu.max.toFixed(1)}%
              </div>
            </div>
            
            <div className="stat-card">
              <h3>Avg Memory</h3>
              <div className="value">
                {metrics.aggregated_metrics.memory.average.toFixed(1)}%
              </div>
              <div className="subtext">
                Max: {metrics.aggregated_metrics.memory.max.toFixed(1)}%
              </div>
            </div>
            
            <div className="stat-card">
              <h3>Total Requests</h3>
              <div className="value">
                {metrics.aggregated_metrics.total_requests.toLocaleString()}
              </div>
              <div className="subtext">Across all servers</div>
            </div>
            
            <div className="stat-card">
              <h3>Responding</h3>
              <div className="value">{metrics.responding_servers}</div>
              <div className="subtext">
                {((metrics.responding_servers / servers.length) * 100).toFixed(1)}% availability
              </div>
            </div>
          </>
        )}
      </div>

      <div className="section">
        <h2 className="section-title">Server Instances</h2>
        <div className="servers-grid">
          {servers.map(server => (
            <div 
              key={server.id} 
              className={`server-card ${server.status}`}
            >
              <div className="server-header">
                <div className="server-id">Server {server.id}</div>
                <span className={`status-badge ${server.status}`}>
                  {server.status}
                </span>
              </div>
              
              <div className="server-metrics">
                <div className="metric-row">
                  <span className="metric-label">Port:</span>
                  <span className="metric-value">{server.port}</span>
                </div>
                
                {server.cpu_percent !== undefined && (
                  <div>
                    <div className="metric-row">
                      <span className="metric-label">CPU:</span>
                      <span className="metric-value">{server.cpu_percent.toFixed(1)}%</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className={`progress-fill ${
                          server.cpu_percent > 80 ? 'high' : 
                          server.cpu_percent > 50 ? 'medium' : ''
                        }`}
                        style={{ width: `${Math.min(server.cpu_percent, 100)}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {server.memory_percent !== undefined && (
                  <div>
                    <div className="metric-row">
                      <span className="metric-label">Memory:</span>
                      <span className="metric-value">
                        {server.memory_mb.toFixed(0)}MB ({server.memory_percent.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className={`progress-fill ${
                          server.memory_percent > 80 ? 'high' : 
                          server.memory_percent > 50 ? 'medium' : ''
                        }`}
                        style={{ width: `${Math.min(server.memory_percent, 100)}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App
