import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    '📥 Fetching repository...',
    '🔍 Bug Detector Agent scanning...',
    '🛠️ Fix Generator Agent working...',
    '🧐 Self-Reviewer Agent validating...'
  ]

  const analyzeRepo = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    setCurrentStep(0)

    // Animate steps
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev < 3 ? prev + 1 : prev))
    }, 4000)

    try {
      const response = await axios.post('https://autoship-agent.onrender.com/analyze', {
        repo_url: url
      })
      setResult(response.data)
    } catch (err) {
      setError('Analysis failed. Please check the URL and try again.')
      console.error(err)
    } finally {
      clearInterval(stepInterval)
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'
    if (score >= 60) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="app">
      {/* Animated Background */}
      <div className="bg-animation">
        <div className="orb orb1"></div>
        <div className="orb orb2"></div>
        <div className="orb orb3"></div>
      </div>

      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="logo">
            <span className="logo-icon">🤖</span>
            <h1 className="logo-text">AutoShip Agent</h1>
          </div>
          <p className="tagline">Autonomous AI-Powered Code Review System</p>
          <div className="badges">
            <span className="badge">✨ 3 AI Agents</span>
            <span className="badge">⚡ Groq Powered</span>
            <span className="badge">🎯 Self-Reviewing</span>
          </div>
        </header>

        {/* Main Form */}
        <div className="card main-card">
          <form onSubmit={analyzeRepo}>
            <div className="input-group">
              <span className="input-icon">🔗</span>
              <input
                type="text"
                className="url-input"
                placeholder="Paste GitHub repository URL..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              className="analyze-btn"
              disabled={loading || !url}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Analyzing...
                </>
              ) : (
                <>🚀 Analyze Repository</>
              )}
            </button>
          </form>

          {/* Example URLs */}
          {!loading && !result && (
            <div className="examples">
              <p className="examples-title">Try these examples:</p>
              <div className="example-chips">
                <button 
                  className="chip" 
                  onClick={() => setUrl('https://github.com/tiangolo/fastapi')}
                >
                  tiangolo/fastapi
                </button>
                <button 
                  className="chip" 
                  onClick={() => setUrl('https://github.com/pallets/flask')}
                >
                  pallets/flask
                </button>
                <button 
                  className="chip" 
                  onClick={() => setUrl('https://github.com/expressjs/express')}
                >
                  expressjs/express
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Loading Steps */}
        {loading && (
          <div className="card loading-card">
            <h3 className="loading-title">🤖 AI Agents Working...</h3>
            <div className="steps">
              {steps.map((step, idx) => (
                <div 
                  key={idx} 
                  className={`step ${idx <= currentStep ? 'active' : ''} ${idx < currentStep ? 'done' : ''}`}
                >
                  <div className="step-indicator">
                    {idx < currentStep ? '✅' : idx === currentStep ? '⚡' : '⏳'}
                  </div>
                  <span className="step-text">{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="card error-card">
            <span className="error-icon">⚠️</span>
            <p>{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="results">
            {/* Repo Info */}
            <div className="card repo-info">
              <span className="repo-label">Analyzed Repository</span>
              <h2 className="repo-name">{result.repository}</h2>
              <div className={`status-badge ${result.analysis.approved ? 'approved' : 'warning'}`}>
                {result.analysis.approved ? '✅ APPROVED' : '⚠️ NEEDS WORK'}
                <span className="confidence">Confidence: {result.analysis.confidence}</span>
              </div>
            </div>

            {/* Metrics Grid */}
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon">📊</div>
                <div className="metric-value" style={{color: getScoreColor(result.analysis.code_quality_score)}}>
                  {result.analysis.code_quality_score}
                </div>
                <div className="metric-label">Code Quality</div>
                <div className="metric-sub">out of 100</div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🐛</div>
                <div className="metric-value" style={{color: '#ef4444'}}>
                  {result.analysis.bugs_found}
                </div>
                <div className="metric-label">Bugs Found</div>
                <div className="metric-sub">critical issues</div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🔒</div>
                <div className="metric-value" style={{color: '#f59e0b'}}>
                  {result.analysis.security_issues}
                </div>
                <div className="metric-label">Security</div>
                <div className="metric-sub">vulnerabilities</div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">⚡</div>
                <div className="metric-value" style={{color: '#3b82f6'}}>
                  {result.analysis.performance_issues}
                </div>
                <div className="metric-label">Performance</div>
                <div className="metric-sub">optimizations</div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🛠️</div>
                <div className="metric-value" style={{color: '#10b981'}}>
                  {result.analysis.fixes_generated}
                </div>
                <div className="metric-label">Fixes Generated</div>
                <div className="metric-sub">auto-corrected</div>
              </div>

              <div className="metric-card">
                <div className="metric-icon">🧐</div>
                <div className="metric-value" style={{color: getScoreColor(result.analysis.review_score)}}>
                  {result.analysis.review_score}
                </div>
                <div className="metric-label">Review Score</div>
                <div className="metric-sub">agent verified</div>
              </div>
            </div>

            {/* Bugs Section */}
            <div className="card details-card">
              <h3 className="section-title">🐛 Bugs Detected</h3>
              {result.details.bugs.bugs.map((bug, idx) => (
                <div key={idx} className={`issue-item severity-${bug.severity}`}>
                  <div className="issue-header">
                    <span className={`severity-badge ${bug.severity}`}>{bug.severity.toUpperCase()}</span>
                    <span className="file-path">{bug.file}:{bug.line}</span>
                  </div>
                  <p className="issue-desc">{bug.description}</p>
                </div>
              ))}
            </div>

            {/* Fixes Section */}
            <div className="card details-card">
              <h3 className="section-title">🛠️ AI-Generated Fixes</h3>
              {result.details.fixes.fixes.map((fix, idx) => (
                <div key={idx} className="fix-item">
                  <div className="fix-header">
                    <span className="fix-file">📄 {fix.file}</span>
                  </div>
                  <p className="fix-issue">🐛 {fix.original_issue}</p>
                  <div className="fix-explanation">
                    <strong>💡 Fix Explanation:</strong>
                    <p>{fix.explanation}</p>
                  </div>
                  <details className="code-details">
                    <summary>View Fixed Code</summary>
                    <pre className="code-block">{fix.fixed_code}</pre>
                  </details>
                </div>
              ))}
            </div>

            {/* Recommendations */}
            <div className="card details-card">
              <h3 className="section-title">💡 Agent Recommendations</h3>
              <ul className="recommendations">
                {result.details.review.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec}</li>
                ))}
              </ul>
            </div>

            {/* Raw JSON */}
            <details className="card json-card">
              <summary>🔍 View Complete JSON Report</summary>
              <pre className="json-block">{JSON.stringify(result, null, 2)}</pre>
            </details>
          </div>
        )}

        {/* Footer */}
        <footer className="footer">
          <p>Built with ❤️ for ChatGPT × Codex Hackathon 2026</p>
          <p className="footer-tech">Powered by Groq • FastAPI • React</p>
        </footer>
      </div>
    </div>
  )
}

export default App
