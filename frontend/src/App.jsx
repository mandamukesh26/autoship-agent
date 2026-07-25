import { useState } from 'react'
import axios from 'axios'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const analyzeRepo = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await axios.post('https://autoship-agent.onrender.com/analyze', {
        repo_url: url
      })
      setResult(response.data)
    } catch (err) {
      setError('Failed to analyze. Check the URL and try again.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#2563eb', textAlign: 'center' }}>🤖 AutoShip Agent</h1>
      <p style={{ textAlign: 'center', color: '#666' }}>AI-powered code review with autonomous bug detection</p>

      <form onSubmit={analyzeRepo} style={{ marginTop: '30px' }}>
        <input
          type="text"
          placeholder="Paste GitHub URL (e.g., https://github.com/tiangolo/fastapi)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '16px',
            borderRadius: '8px',
            border: '1px solid #ddd',
            marginBottom: '10px'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: loading ? '#93c5fd' : '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? '🔍 Agents Analyzing...' : '🚀 Analyze Repository'}
        </button>
      </form>

      {loading && (
        <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#f3f4f6', borderRadius: '8px', textAlign: 'center' }}>
          <p>🕐 Step 1/4: Fetching repository...</p>
          <p>🕑 Step 2/4: Bug Detector Agent running...</p>
          <p>🕒 Step 3/4: Fix Generator Agent working...</p>
          <p>🕓 Step 4/4: Self-Reviewer Agent checking...</p>
        </div>
      )}

      {error && (
        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#fee2e2', color: '#dc2626', borderRadius: '8px' }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '30px' }}>
          <h2 style={{ color: '#1f2937' }}>📊 Analysis Results</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '20px' }}>
            <div style={{ padding: '15px', backgroundColor: '#dbeafe', borderRadius: '8px', textAlign: 'center' }}>
              <h3 style={{ margin: '0', color: '#1e40af' }}>{result.analysis.code_quality_score}/100</h3>
              <p style={{ margin: '5px 0 0 0', color: '#1e3a8a' }}>Code Quality</p>
            </div>
            
            <div style={{ padding: '15px', backgroundColor: '#fecaca', borderRadius: '8px', textAlign: 'center' }}>
              <h3 style={{ margin: '0', color: '#991b1b' }}>{result.analysis.bugs_found}</h3>
              <p style={{ margin: '5px 0 0 0', color: '#7f1d1d' }}>Bugs Found</p>
            </div>
            
            <div style={{ padding: '15px', backgroundColor: '#bbf7d0', borderRadius: '8px', textAlign: 'center' }}>
              <h3 style={{ margin: '0', color: '#166534' }}>{result.analysis.fixes_generated}</h3>
              <p style={{ margin: '5px 0 0 0', color: '#14532d' }}>Fixes Generated</p>
            </div>
            
            <div style={{ padding: '15px', backgroundColor: '#fde68a', borderRadius: '8px', textAlign: 'center' }}>
              <h3 style={{ margin: '0', color: '#92400e' }}>{result.analysis.review_score}/100</h3>
              <p style={{ margin: '5px 0 0 0', color: '#78350f' }}>Review Score</p>
            </div>
          </div>

          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: result.analysis.approved ? '#d1fae5' : '#fee2e2', borderRadius: '8px', textAlign: 'center' }}>
            <h3 style={{ margin: '0', color: result.analysis.approved ? '#065f46' : '#dc2626' }}>
              {result.analysis.approved ? '✅ APPROVED' : '⚠️ NEEDS WORK'}
            </h3>
            <p style={{ margin: '5px 0 0 0', color: '#4b5563' }}>
              Confidence: {result.analysis.confidence}
            </p>
          </div>

          <details style={{ marginTop: '20px' }}>
            <summary style={{ cursor: 'pointer', padding: '10px', backgroundColor: '#f3f4f6', borderRadius: '8px', fontWeight: 'bold' }}>
              View Detailed Report (JSON)
            </summary>
            <pre style={{ backgroundColor: '#1f2937', color: '#e5e7eb', padding: '15px', borderRadius: '8px', overflow: 'auto', fontSize: '12px' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  )
}

export default App
