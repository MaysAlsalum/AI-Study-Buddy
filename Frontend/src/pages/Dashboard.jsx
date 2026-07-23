import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'
import { buildState } from '../data/mockData.js'

export default function Dashboard() {
  const nav = useNavigate()
  const { setAppState, setUser } = useApp()

  const [file, setFile]           = useState(null)
  const [goal, setGoal]           = useState('quiz')
  const [studyDays, setStudyDays] = useState(5)
  const [loading, setLoading]     = useState(false)
  const [dragOver, setDragOver]   = useState(false)
  const inputRef = useRef(null)

  function handleFile(f) {
    if (f && f.type === 'application/pdf') setFile(f)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    handleFile(f)
  }

  function handleProcess() {
    if (!file || loading) return
    setLoading(true)
    setTimeout(() => {
      setAppState(buildState(file.name, studyDays, goal))
      setLoading(false)
      nav('/results')
    }, 1400)
  }

  function handleSignOut() {
    setUser(null)
    nav('/')
  }

  const isStudyPlan = goal === 'study_plan'

  return (
    <>
      {/* ── Navbar ─────────────────────────────────────────── */}
      <nav className="app-nav">
        <div className="app-nav-inner">
          <span className="app-nav-brand">AI Study Buddy</span>
          <span className="app-nav-file">Dashboard</span>
        </div>
      </nav>

      {/* ── Page header ────────────────────────────────────── */}
      <div className="dash-hero">
        <h1>Process a Study Document</h1>
        <p>
          Upload your material, choose your goal, and let the AI agents
          generate exactly what you need.
        </p>
      </div>

      {/* ── Body ───────────────────────────────────────────── */}
      <div className="dash-body">
        <div className="dash-grid">
          {/* Upload card */}
          <div className="dash-card">
            <span className="card-eyebrow">Study Document</span>
            <span className="card-hint">PDF format · max 200 MB</span>

            <div
              className={`dropzone${dragOver ? ' drag-over' : ''}`}
              onClick={() => inputRef.current.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && inputRef.current.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".pdf"
                hidden
                onChange={(e) => handleFile(e.target.files[0])}
              />
              <span className="dropzone-icon">📄</span>
              <p className="dropzone-text">
                <strong>Click to browse</strong> or drag and drop
              </p>
              <p className="dropzone-sub">PDF files only</p>
            </div>

            {file && (
              <div className="file-chip">
                <span className="file-chip-name">{file.name}</span>
                <span className="file-chip-size">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>
            )}
          </div>

          {/* Config card */}
          <div className="dash-card">
            <span className="card-eyebrow">Session Configuration</span>

            <span className="field-label">Output Goal</span>
            <span className="field-hint">
              The AI generates only the selected output.
            </span>

            <div className="radio-group">
              <label className="radio-option">
                <input
                  type="radio"
                  name="goal"
                  value="quiz"
                  checked={goal === 'quiz'}
                  onChange={() => setGoal('quiz')}
                />
                <span>Generate Quiz</span>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  name="goal"
                  value="study_plan"
                  checked={goal === 'study_plan'}
                  onChange={() => setGoal('study_plan')}
                />
                <span>Generate Study Plan</span>
              </label>
            </div>

            <span className="field-label" style={{ marginTop: '8px' }}>
              Study Days
            </span>
            <span className="field-hint">
              Days available for your plan (1–30). Applies to Study Plan only.
            </span>

            <input
              type="number"
              className="number-input"
              min={1}
              max={30}
              value={studyDays}
              onChange={(e) =>
                setStudyDays(Math.min(30, Math.max(1, Number(e.target.value))))
              }
              disabled={!isStudyPlan}
            />
          </div>
        </div>

        {/* Process button */}
        <div className="dash-actions">
          <button
            className="btn"
            style={{ minWidth: 220 }}
            disabled={!file || loading}
            onClick={handleProcess}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analyzing…
              </>
            ) : (
              'Process Document'
            )}
          </button>

          {!file && (
            <p className="dash-hint">Upload a PDF file to enable processing.</p>
          )}

          {loading && (
            <div className="processing-overlay">
              <div className="processing-spinner" />
              Analyzing document with AI agents…
            </div>
          )}
        </div>

        {/* Sign out */}
        <div className="dash-signout">
          <button className="btn btn-sm" onClick={handleSignOut}>
            Sign Out
          </button>
        </div>
      </div>
    </>
  )
}
