import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'

function SecurityBanner({ security }) {
  const { is_safe = true, warnings = [], risk_level: level = 'Low' } = security

  const config = {
    Low:    { cls: 'sec-card-safe',   icon: '✓', badge: 'Safe',          title: 'Document Passed Security Inspection' },
    Medium: { cls: 'sec-card-medium', icon: '⚠', badge: 'Medium Risk',   title: 'Security Warnings Detected' },
    High:   { cls: 'sec-card-high',   icon: '✕', badge: 'High Risk',     title: 'Potential Injection Detected' },
  }

  const { cls, icon, badge, title } = config[level] ?? config.Low

  return (
    <div className={`sec-card ${cls}`}>
      <div className="sec-card-header">
        <div className="sec-card-icon-wrap">
          <span className="sec-card-icon">{icon}</span>
        </div>
        <div className="sec-card-info">
          <div className="sec-card-top">
            <span className="sec-card-badge">{badge}</span>
            <span className="sec-card-label">PDF Security Scan</span>
          </div>
          <p className="sec-card-title">{title}</p>
        </div>
      </div>

      {warnings.length > 0 && (
        <div className="sec-card-warnings">
          <span className="sec-warnings-label">Warnings</span>
          {warnings.map((w, i) => (
            <div key={i} className="sec-warning-item">
              <span className="sec-warning-dot" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      {level === 'Low' && (
        <p className="sec-card-ok">
          All inputs were validated and sanitised before AI processing. No injection patterns detected.
        </p>
      )}
    </div>
  )
}

export default function SummaryPage() {
  const nav = useNavigate()
  const { summaryData, setSummaryData, setQuizData, setPlanData, setUser } = useApp()

  if (!summaryData) {
    nav('/dashboard', { replace: true })
    return null
  }

  const {
    file_name   = 'Document',
    summary     = '',
    key_topics  = [],
    definitions = [],
    security    = { is_safe: true, risk_level: 'Low', warnings: [] },
  } = summaryData

  function handleNew() {
    setSummaryData(null)
    setQuizData(null)
    setPlanData(null)
    nav('/dashboard')
  }

  function handleSignOut() {
    setSummaryData(null)
    setQuizData(null)
    setPlanData(null)
    setUser(null)
    nav('/')
  }

  return (
    <>
      {/* Navbar */}
      <nav className="app-nav">
        <div className="app-nav-inner">
          <span className="app-nav-brand">AI Study Buddy</span>
          <span className="app-nav-file">{file_name}</span>
        </div>
      </nav>

      {/* Action bar */}
      <div className="results-actions">
        <button className="btn btn-sm" onClick={handleNew}>New Document</button>
        <button className="btn btn-sm btn-ghost" onClick={handleSignOut}>Sign Out</button>
      </div>
      <hr className="results-divider" />

      {/* Content */}
      <div className="results-content">
        <SecurityBanner security={security} />

        {/* Summary */}
        <div className="res-section">
          <span className="res-eyebrow">Document Analysis</span>
          <h2 className="res-title">Summary</h2>
          <div className="res-card">
            <p className="summary-body">{summary}</p>
          </div>
        </div>

        {/* Key Topics */}
        <div className="res-section">
          <span className="res-eyebrow">Extracted Concepts</span>
          <h2 className="res-title">Key Topics</h2>
          <div className="res-card pills">
            {key_topics.map((t) => <span key={t} className="pill">{t}</span>)}
          </div>
        </div>

        {/* Definitions */}
        {definitions.length > 0 && (
          <div className="res-section">
            <span className="res-eyebrow">Glossary</span>
            <h2 className="res-title">Definitions</h2>
            <div className="res-card def-table">
              {definitions.map((d) => (
                <div key={d.term} className="def-row">
                  <div className="def-term">{d.term}</div>
                  <div className="def-body">{d.definition}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 2 — choose output */}
        <div className="res-section">
          <span className="res-eyebrow">Step 2 — Choose Your Output</span>
          <h2 className="res-title">What do you want to generate?</h2>
          <div className="action-cards">
            <button className="action-card" onClick={() => nav('/quiz')}>
              <span className="action-card-icon">🧠</span>
              <span className="action-card-title">Generate Quiz</span>
              <span className="action-card-desc">
                Adaptive MCQ and short-answer questions to test your knowledge.
              </span>
            </button>
            <button className="action-card" onClick={() => nav('/study-plan')}>
              <span className="action-card-icon">📅</span>
              <span className="action-card-title">Create Study Plan</span>
              <span className="action-card-desc">
                A personalised day-by-day schedule with spaced repetition.
              </span>
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
