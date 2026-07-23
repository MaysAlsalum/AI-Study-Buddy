import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'

/* ── Security banner ─────────────────────────────────────────── */
function SecurityBanner({ security }) {
  const { warnings = [], risk_level: level = 'Low' } = security
  if (!warnings.length && level === 'Low') return null

  const cls = { Low: 'sec-low', Medium: 'sec-med', High: 'sec-high' }[level] ?? 'sec-low'
  return (
    <div className={`sec-banner ${cls}`}>
      <span className="sec-label">Security · {level} Risk</span>
      {warnings.map((w, i) => (
        <span key={i} className="sec-warn">{w}</span>
      ))}
    </div>
  )
}

/* ── Summary ─────────────────────────────────────────────────── */
function Summary({ text }) {
  return (
    <div className="res-section">
      <span className="res-eyebrow">Document Analysis</span>
      <h2 className="res-title">Summary</h2>
      <div className="res-card">
        <p className="summary-body">{text}</p>
      </div>
    </div>
  )
}

/* ── Key Topics ──────────────────────────────────────────────── */
function Topics({ topics }) {
  return (
    <div className="res-section">
      <span className="res-eyebrow">Extracted Concepts</span>
      <h2 className="res-title">Key Topics</h2>
      <div className="res-card pills">
        {topics.map((t) => (
          <span key={t} className="pill">{t}</span>
        ))}
      </div>
    </div>
  )
}

/* ── Definitions ─────────────────────────────────────────────── */
function Definitions({ defs }) {
  return (
    <div className="res-section">
      <span className="res-eyebrow">Glossary</span>
      <h2 className="res-title">Definitions</h2>
      <div className="res-card def-table">
        {defs.map((d) => (
          <div key={d.term} className="def-row">
            <div className="def-term">{d.term}</div>
            <div className="def-body">{d.definition}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ── Quiz ────────────────────────────────────────────────────── */
function Quiz({ quiz }) {
  const [revealed, setRevealed] = useState(new Set())

  function toggle(i) {
    setRevealed((prev) => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  return (
    <div className="res-section">
      <span className="res-eyebrow">Assessment</span>
      <h2 className="res-title">Quiz</h2>

      {quiz.map((q, i) => (
        <div key={i}>
          <div className="quiz-card">
            <span className="q-num">Question {i + 1}</span>
            {q.type === 'short_answer' && (
              <span className="q-type-badge">Short Answer</span>
            )}
            <p className="q-text">{q.question}</p>
            {q.type !== 'short_answer' && Array.isArray(q.choices) && (
              <div className="choices">
                {q.choices.map((c, j) => (
                  <div key={j} className="choice">
                    <span className="choice-letter">{String.fromCharCode(65 + j)}</span>
                    <span className="choice-text">{c}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="quiz-reveal-row">
            <button className="btn" onClick={() => toggle(i)}>
              {revealed.has(i) ? 'Hide Answer' : 'Reveal Answer'}
            </button>
          </div>

          {revealed.has(i) && (
            <div className="answer-reveal">
              <span className="ans-label">Correct Answer</span>
              <p className="ans-text">{q.correct_answer}</p>
              <p className="ans-explain">{q.explanation}</p>
            </div>
          )}

          {i < quiz.length - 1 && <div className="quiz-sep" />}
        </div>
      ))}
    </div>
  )
}

/* ── Study Plan ──────────────────────────────────────────────── */
function StudyPlan({ plan }) {
  return (
    <div className="res-section">
      <span className="res-eyebrow">Learning Schedule</span>
      <h2 className="res-title">Study Plan</h2>
      <div className="plan-grid">
        {plan.map((entry) => (
          <div key={entry.day} className="plan-row">
            <div className="plan-day-col">
              <span className="plan-day-label">Day</span>
              <span className="plan-day-num">{entry.day}</span>
            </div>
            <div className="plan-topics-col">
              {entry.topics.map((t) => (
                <span
                  key={t}
                  className={`plan-topic-chip${t.startsWith('Review:') ? ' review-chip' : ''}`}
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ── Results Page ────────────────────────────────────────────── */
export default function Results() {
  const nav = useNavigate()
  const { appState, setAppState } = useApp()

  if (!appState) {
    nav('/dashboard', { replace: true })
    return null
  }

  const {
    file_name   = 'Document',
    goal        = 'quiz',
    summary     = '',
    key_topics  = [],
    definitions = [],
    quiz        = [],
    study_plan  = [],
    security    = { is_safe: true, risk_level: 'Low', warnings: [] },
  } = appState

  function handleNew() {
    setAppState(null)
    nav('/dashboard')
  }

  function handleSignOut() {
    setAppState(null)
    nav('/')
  }

  return (
    <>
      {/* ── Navbar ─────────────────────────────────────────── */}
      <nav className="app-nav">
        <div className="app-nav-inner">
          <span className="app-nav-brand">AI Study Buddy</span>
          <span className="app-nav-file">{file_name}</span>
        </div>
      </nav>

      {/* ── Action bar ─────────────────────────────────────── */}
      <div className="results-actions">
        <button className="btn btn-sm" onClick={handleNew}>
          New Document
        </button>
        <button className="btn btn-sm btn-ghost" onClick={handleSignOut}>
          Sign Out
        </button>
      </div>

      <hr className="results-divider" />

      {/* ── Content ────────────────────────────────────────── */}
      <div className="results-content">
        <SecurityBanner security={security} />
        <Summary text={summary} />
        <Topics topics={key_topics} />
        <Definitions defs={definitions} />

        {goal === 'quiz' && quiz.length > 0 && <Quiz quiz={quiz} />}
        {goal === 'study_plan' && study_plan.length > 0 && (
          <StudyPlan plan={study_plan} />
        )}
      </div>
    </>
  )
}
