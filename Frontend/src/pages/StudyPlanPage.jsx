import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

function formatDate(base, offsetDays) {
  const d = new Date(base)
  d.setDate(d.getDate() + offsetDays)
  return `${DAYS[d.getDay()]} ${d.getDate()} ${MONTHS[d.getMonth()]}`
}

export default function StudyPlanPage() {
  const nav = useNavigate()
  const { summaryData } = useApp()

  const [studyDays, setStudyDays]   = useState(5)
  const [startDate, setStartDate]   = useState(() => new Date().toISOString().slice(0, 10))
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)
  const [plan, setPlan]             = useState(null)
  const [completed, setCompleted]   = useState(new Set()) // set of completed day numbers

  if (!summaryData) {
    nav('/dashboard', { replace: true })
    return null
  }

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    setPlan(null)
    setCompleted(new Set())

    try {
      const res = await fetch('/api/study-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          key_topics: summaryData.key_topics,
          study_days: studyDays,
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setError(err.detail || `Server error (${res.status}).`)
        return
      }
      const data = await res.json()
      setPlan(data.study_plan)
    } catch {
      setError('Could not reach the backend. Make sure the server is running on port 8080.')
    } finally {
      setLoading(false)
    }
  }

  function toggleDay(day) {
    setCompleted((prev) => {
      const next = new Set(prev)
      next.has(day) ? next.delete(day) : next.add(day)
      return next
    })
  }

  // ── Stats ─────────────────────────────────────────────────────
  const stats = useMemo(() => {
    if (!plan) return null
    const totalHours = plan.reduce((s, e) => s + (e.estimated_hours || 0), 0)
    const allTopics  = new Set(plan.flatMap((e) => e.topics.filter((t) => !t.startsWith('Review:'))))
    const reviewDays = plan.filter((e) => e.topics.some((t) => t.startsWith('Review:'))).length
    return {
      totalHours: totalHours.toFixed(1),
      avgHours:   (totalHours / plan.length).toFixed(1),
      uniqueTopics: allTopics.size,
      reviewDays,
    }
  }, [plan])

  const completedCount = completed.size
  const progressPct    = plan ? Math.round((completedCount / plan.length) * 100) : 0

  return (
    <>
      <nav className="app-nav">
        <div className="app-nav-inner">
          <span className="app-nav-brand">AI Study Buddy</span>
          <span className="app-nav-file">{summaryData.file_name}</span>
        </div>
      </nav>

      <div className="results-actions">
        <button className="btn btn-sm" onClick={() => nav('/summary')}>← Back to Summary</button>
        <button className="btn btn-sm" onClick={() => nav('/dashboard')}>New Document</button>
      </div>
      <hr className="results-divider" />

      <div className="results-content">

        {/* ── Config ─────────────────────────────────────────── */}
        <div className="res-section">
          <span className="res-eyebrow">Study Plan Configuration</span>
          <h2 className="res-title">Set Up Your Schedule</h2>
          <div className="quiz-config-card">
            <div className="quiz-config-row plan-config-row">
              <div className="quiz-config-field">
                <label className="field-label">Available Study Days</label>
                <span className="field-hint">How many days you have (1–30)</span>
                <input
                  type="number"
                  className="number-input"
                  min={1} max={30}
                  value={studyDays}
                  onChange={(e) => setStudyDays(Math.min(30, Math.max(1, Number(e.target.value))))}
                />
              </div>
              <div className="quiz-config-field">
                <label className="field-label">Start Date</label>
                <span className="field-hint">When you plan to start studying</span>
                <input
                  type="date"
                  className="number-input"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
            </div>

            <div style={{ marginTop: '24px' }}>
              <button className="btn" onClick={handleGenerate} disabled={loading}>
                {loading ? <><span className="spinner" />Generating plan…</> : 'Generate Study Plan'}
              </button>
            </div>

            {error && <p style={{ color: '#DC2626', marginTop: '12px', fontSize: '14px' }}>{error}</p>}
            {loading && (
              <div className="processing-overlay" style={{ marginTop: '16px' }}>
                <div className="processing-spinner" />
                Building your personalised schedule with spaced repetition…
              </div>
            )}
          </div>
        </div>

        {plan && plan.length > 0 && (
          <>
            {/* ── Stats cards ──────────────────────────────────── */}
            <div className="res-section">
              <span className="res-eyebrow">Plan Overview</span>
              <h2 className="res-title">Your {plan.length}-Day Study Plan</h2>
              <div className="plan-stats">
                <div className="plan-stat-card">
                  <span className="plan-stat-value">{plan.length}</span>
                  <span className="plan-stat-label">Study Days</span>
                </div>
                <div className="plan-stat-card">
                  <span className="plan-stat-value">{stats.totalHours}h</span>
                  <span className="plan-stat-label">Total Hours</span>
                </div>
                <div className="plan-stat-card">
                  <span className="plan-stat-value">{stats.avgHours}h</span>
                  <span className="plan-stat-label">Avg / Day</span>
                </div>
                <div className="plan-stat-card">
                  <span className="plan-stat-value">{stats.uniqueTopics}</span>
                  <span className="plan-stat-label">Unique Topics</span>
                </div>
                <div className="plan-stat-card">
                  <span className="plan-stat-value">{stats.reviewDays}</span>
                  <span className="plan-stat-label">Review Days</span>
                </div>
              </div>
            </div>

            {/* ── Progress tracker ─────────────────────────────── */}
            <div className="res-section">
              <span className="res-eyebrow">Your Progress</span>
              <div className="progress-card">
                <div className="progress-header">
                  <span className="progress-title">
                    {completedCount} of {plan.length} days completed
                  </span>
                  <span className="progress-pct">{progressPct}%</span>
                </div>
                <div className="progress-bar-wrap">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
                {progressPct === 100 && (
                  <p className="progress-done">
                    Congratulations — you have completed your full study plan!
                  </p>
                )}
              </div>
            </div>

            {/* ── Day-by-day plan ──────────────────────────────── */}
            <div className="res-section">
              <span className="res-eyebrow">Daily Schedule</span>
              <div className="plan-grid">
                {plan.map((entry) => {
                  const done    = completed.has(entry.day)
                  const dateStr = startDate ? formatDate(startDate, entry.day - 1) : null
                  const isReviewDay = entry.topics.every((t) => t.startsWith('Review:'))

                  return (
                    <div
                      key={entry.day}
                      className={`plan-row${done ? ' plan-row-done' : ''}`}
                    >
                      {/* Day column */}
                      <div className={`plan-day-col${done ? ' plan-day-done' : ''}`}>
                        <span className="plan-day-label">
                          {isReviewDay ? 'Review' : 'Day'}
                        </span>
                        <span className="plan-day-num">{entry.day}</span>
                        {entry.estimated_hours > 0 && (
                          <span className="plan-day-hours">{entry.estimated_hours}h</span>
                        )}
                        {dateStr && (
                          <span className="plan-day-date">{dateStr}</span>
                        )}
                      </div>

                      {/* Topics column */}
                      <div className="plan-topics-col">
                        <div className="plan-meta">
                          {entry.difficulty && (
                            <span className={`difficulty-badge diff-${entry.difficulty}`}>
                              {entry.difficulty}
                            </span>
                          )}
                          {entry.estimated_hours > 0 && (
                            <span className="plan-hours-badge">
                              {entry.estimated_hours} hr{entry.estimated_hours !== 1 ? 's' : ''}
                            </span>
                          )}
                        </div>
                        <div className="plan-chips">
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

                      {/* Completion checkbox */}
                      <div className="plan-check-col">
                        <button
                          className={`day-check-btn${done ? ' day-check-done' : ''}`}
                          onClick={() => toggleDay(entry.day)}
                          title={done ? 'Mark as incomplete' : 'Mark as complete'}
                        >
                          {done ? '✓' : ''}
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </>
  )
}
