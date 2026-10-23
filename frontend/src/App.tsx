import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'error'>('checking')

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/v1/health')
        if (response.ok) {
          setHealthStatus('healthy')
        } else {
          setHealthStatus('error')
        }
      } catch {
        setHealthStatus('error')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const email = 'alanvo@gmail.com'

  return (
    <div className="app">
      <header className="app-header">
        <h1>Tensor Forge 144</h1>
        <p>Jailbreak Evaluation Framework for LLMs</p>
      </header>

      <main className="app-main">
        <div className="card">
          <h2>System Status</h2>
          <div>
            <span className={`status-badge status-${healthStatus}`}>
              {healthStatus === 'checking' ? 'Checking...' : healthStatus === 'healthy' ? 'Healthy' : 'Error'}
            </span>
          </div>
        </div>

        <div className="card">
          <h2>Quick Actions</h2>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <button className="btn btn-primary" disabled>Manage Prompts</button>
            <button className="btn btn-secondary" disabled>Run Evaluation</button>
            <button className="btn btn-secondary" disabled>View Results</button>
          </div>
          <p style={{ marginTop: '1rem', color: '#666', fontSize: '0.875rem' }}>
            Features coming in next sprint: Prompt Management, Model-Specific Prompts, Jailbreak Evaluation
          </p>
        </div>

        <div className="card">
          <h2>About</h2>
          <p>
            Tensor Forge 144 is a jailbreak evaluation framework for Large Language Models.
            It provides model-specific prompt management, deterministic evaluation against
            labeled datasets, and comprehensive metrics for AI safety research.
          </p>
          <ul style={{ marginTop: '1rem', paddingLeft: '1.5rem', color: '#4b5563' }}>
            <li>Model-specific prompt templates (default: "小码辉")</li>
            <li>Deterministic jailbreak evaluation engine</li>
            <li>Export results for analysis</li>
            <li>OIDC authentication with Keycloak</li>
            <li>Multi-provider LLM support (OpenAI, Anthropic, Gemini, Ollama)</li>
          </ul>
        </div>
      </main>

      <footer className="app-footer">
        <p>Tensor Forge 144 \u00a9 2026 Alan Vo {email} | AI & Machine Learning</p>
      </footer>
    </div>
  )
}

export default App
