import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'

/* ── Single question component ───────────────────────────────── */
function QuizQuestion({ q, index, selected, onSelect, onShortGrade }) {
  const isMcq = q.type !== 'short_answer'

  // MCQ: find correct choice index
  const correctIdx = isMcq && Array.isArray(q.choices)
    ? q.choices.indexOf(q.correct_answer)
    : -1

  function choiceClass(j) {
    if (selected === undefined) return 'choice choice-btn'
    if (j === correctIdx)       return 'choice choice-btn choice-correct'
    if (j === selected)         return 'choice choice-btn choice-wrong'
    return 'choice choice-btn choice-dim'
  }

  // Short-answer local state
  const [userAnswer, setUserAnswer] = useState('')
  const [submitted, setSubmitted]   = useState(false)
  const [grade, setGrade]           = useState(null) // 'correct' | 'wrong'

  function handleSubmit() {
    if (userAnswer.trim()) setSubmitted(true)
  }

  function handleGrade(g) {
    setGrade(g)
    onShortGrade(index, g)
  }

  const mcqAnswered = isMcq && selected !== undefined
  const isCorrectMcq = selected === correctIdx

  return (
    <div className={`quiz-card${mcqAnswered ? (isCorrectMcq ? ' card-correct' : ' card-wrong') : ''}`}>
      {/* Header */}
      <div className="q-header">
        <span className="q-num">Question {index + 1}</span>
        {!isMcq && <span className="q-type-badge">Short Answer</span>}
        {mcqAnswered && (
          <span className={`q-result-badge ${isCorrectMcq ? 'badge-correct' : 'badge-wrong'}`}>
            {isCorrectMcq ? '✓ Correct' : '✗ Incorrect'}
          </span>
        )}
        {!isMcq && grade && (
          <span className={`q-result-badge ${grade === 'correct' ? 'badge-correct' : 'badge-wrong'}`}>
            {grade === 'correct' ? '✓ Self-marked correct' : '✗ Self-marked wrong'}
          </span>
        )}
      </div>

      <p className="q-text">{q.question}</p>

      {/* ── MCQ choices ──────────────────────────────────────── */}
      {isMcq && Array.isArray(q.choices) && (
        <div className="choices">
          {q.choices.map((c, j) => (
            <button
              key={j}
              className={choiceClass(j)}
              onClick={() => !mcqAnswered && onSelect(index, j)}
              disabled={mcqAnswered}
            >
              <span className="choice-letter">{String.fromCharCode(65 + j)}</span>
              <span className="choice-text">{c}</span>
              {mcqAnswered && j === correctIdx && <span className="choice-check">✓</span>}
            </button>
          ))}
        </div>
      )}

      {/* MCQ explanation */}
      {mcqAnswered && (
        <div className={`answer-reveal${isCorrectMcq ? '' : ' answer-reveal-wrong'}`}>
          <span className="ans-label">
            {isCorrectMcq ? 'Correct!' : `Correct Answer: ${q.correct_answer}`}
          </span>
          <p className="ans-explain">{q.explanation}</p>
        </div>
      )}

      {/* ── Short answer ─────────────────────────────────────── */}
      {!isMcq && (
        <div className="short-answer-area">
          {!submitted ? (
            <>
              <label className="field-label" style={{ marginBottom: 8 }}>
                Your Answer
              </label>
              <textarea
                className="sa-textarea"
                placeholder="Write your answer here…"
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                rows={4}
              />
              <div style={{ marginTop: 12 }}>
                <button
                  className="btn btn-sm"
                  onClick={handleSubmit}
                  disabled={!userAnswer.trim()}
                >
                  Submit &amp; Reveal Answer
                </button>
              </div>
            </>
          ) : (
            <>
              {/* Side-by-side comparison */}
              <div className="sa-compare">
                <div className="sa-compare-col sa-yours">
                  <span className="sa-col-label">Your Answer</span>
                  <p className="sa-col-text">{userAnswer}</p>
                </div>
                <div className="sa-compare-col sa-model">
                  <span className="sa-col-label">Model Answer</span>
                  <p className="sa-col-text">{q.correct_answer}</p>
                </div>
              </div>

              {q.explanation && (
                <div className="answer-reveal" style={{ marginTop: 12 }}>
                  <span className="ans-label">Explanation</span>
                  <p className="ans-explain">{q.explanation}</p>
                </div>
              )}

              {/* Self-grade */}
              {!grade ? (
                <div className="self-grade-row">
                  <span className="self-grade-label">How did you do?</span>
                  <button className="grade-btn grade-correct" onClick={() => handleGrade('correct')}>
                    ✓ I got it right
                  </button>
                  <button className="grade-btn grade-wrong" onClick={() => handleGrade('wrong')}>
                    ✗ I got it wrong
                  </button>
                </div>
              ) : (
                <div className={`answer-reveal${grade === 'wrong' ? ' answer-reveal-wrong' : ''}`}
                  style={{ marginTop: 12 }}>
                  <span className="ans-label">
                    {grade === 'correct' ? 'Marked as correct' : 'Marked as incorrect'}
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

/* ── Quiz Page ───────────────────────────────────────────────── */
export default function QuizPage() {
  const nav = useNavigate()
  const { summaryData } = useApp()

  const [numMcq, setNumMcq]         = useState(3)
  const [numShort, setNumShort]     = useState(2)
  const [difficulty, setDifficulty] = useState('medium')
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)
  const [quiz, setQuiz]             = useState(null)
  const [selected, setSelected]     = useState({})        // { [i]: choiceIdx } for MCQ
  const [shortGrades, setShortGrades] = useState({})      // { [i]: 'correct'|'wrong' }

  if (!summaryData) {
    nav('/dashboard', { replace: true })
    return null
  }

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    setQuiz(null)
    setSelected({})
    setShortGrades({})

    try {
      const res = await fetch('/api/quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          summary:    summaryData.summary,
          key_topics: summaryData.key_topics,
          num_mcq:    numMcq,
          num_short:  numShort,
          difficulty,
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setError(err.detail || `Server error (${res.status}).`)
        return
      }
      const data = await res.json()
      setQuiz(data.quiz)
    } catch {
      setError('Could not reach the backend. Make sure the server is running on port 8080.')
    } finally {
      setLoading(false)
    }
  }

  function handleSelect(qIdx, choiceIdx) {
    setSelected((prev) => ({ ...prev, [qIdx]: choiceIdx }))
  }

  function handleShortGrade(qIdx, grade) {
    setShortGrades((prev) => ({ ...prev, [qIdx]: grade }))
  }

  // ── Score calculation ─────────────────────────────────────────
  const totalQ = quiz ? quiz.length : 0

  const mcqCorrect = quiz
    ? quiz.filter((q, i) => {
        if (q.type === 'short_answer') return false
        const correctIdx = q.choices?.indexOf(q.correct_answer) ?? -1
        return selected[i] === correctIdx
      }).length
    : 0

  const shortCorrect = Object.values(shortGrades).filter((g) => g === 'correct').length

  const totalCorrect = mcqCorrect + shortCorrect

  const mcqAnswered   = quiz ? quiz.filter((q, i) => q.type !== 'short_answer' && selected[i] !== undefined).length : 0
  const shortAnswered = Object.keys(shortGrades).length
  const totalAnswered = mcqAnswered + shortAnswered

  const pct = totalQ > 0 ? Math.round((totalCorrect / totalQ) * 100) : 0

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
          <span className="res-eyebrow">Quiz Configuration</span>
          <h2 className="res-title">Customise Your Quiz</h2>
          <div className="quiz-config-card">
            <div className="quiz-config-row">
              <div className="quiz-config-field">
                <label className="field-label">Multiple Choice Questions</label>
                <span className="field-hint">1–10 MCQ questions</span>
                <input
                  type="number"
                  className="number-input"
                  min={1} max={10}
                  value={numMcq}
                  onChange={(e) => setNumMcq(Math.min(10, Math.max(1, Number(e.target.value))))}
                />
              </div>
              <div className="quiz-config-field">
                <label className="field-label">Short Answer Questions</label>
                <span className="field-hint">0–5 short-answer questions</span>
                <input
                  type="number"
                  className="number-input"
                  min={0} max={5}
                  value={numShort}
                  onChange={(e) => setNumShort(Math.min(5, Math.max(0, Number(e.target.value))))}
                />
              </div>
              <div className="quiz-config-field">
                <label className="field-label">Difficulty</label>
                <span className="field-hint">Question difficulty level</span>
                <select
                  className="number-input"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            <div style={{ marginTop: '24px' }}>
              <button className="btn" onClick={handleGenerate} disabled={loading}>
                {loading ? <><span className="spinner" />Generating quiz…</> : 'Generate Quiz'}
              </button>
            </div>

            {error && <p style={{ color: '#DC2626', marginTop: '12px', fontSize: '14px' }}>{error}</p>}
            {loading && (
              <div className="processing-overlay" style={{ marginTop: '16px' }}>
                <div className="processing-spinner" />
                AI is generating your quiz questions…
              </div>
            )}
          </div>
        </div>

        {/* ── Score dashboard ─────────────────────────────────── */}
        {quiz && quiz.length > 0 && (
          <div className="res-section">
            <div className="quiz-header-row">
              <div>
                <span className="res-eyebrow">Assessment</span>
                <h2 className="res-title">Your Quiz — {quiz.length} Questions</h2>
              </div>

              {/* Score summary */}
              <div className="score-dashboard">
                <div className="score-main">
                  <span className="score-label">Total Score</span>
                  <span className="score-value">{totalCorrect}<span className="score-total">/{totalQ}</span></span>
                  <span className="score-pct">{pct}%</span>
                </div>
                <div className="score-breakdown">
                  <div className="score-row">
                    <span className="score-row-label">MCQ</span>
                    <span className="score-row-val">{mcqCorrect}/{numMcq} · {mcqAnswered} answered</span>
                  </div>
                  {numShort > 0 && (
                    <div className="score-row">
                      <span className="score-row-label">Short Answer</span>
                      <span className="score-row-val">{shortCorrect}/{numShort} · {shortAnswered} graded</span>
                    </div>
                  )}
                </div>
                {/* Progress bar */}
                <div className="score-progress-wrap">
                  <div
                    className="score-progress-fill"
                    style={{ width: `${totalAnswered > 0 ? (totalCorrect / totalAnswered) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="quiz-list">
              {quiz.map((q, i) => (
                <QuizQuestion
                  key={i}
                  q={q}
                  index={i}
                  selected={selected[i]}
                  onSelect={handleSelect}
                  onShortGrade={handleShortGrade}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  )
}
