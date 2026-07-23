import { useNavigate } from 'react-router-dom'

const FEATURES = [
  {
    num: '01',
    title: 'Intelligent Summarization',
    desc: 'Automatically condenses uploaded documents into structured, topic-focused summaries that highlight the most critical concepts for efficient review.',
  },
  {
    num: '02',
    title: 'AI-Powered Assessments',
    desc: 'Generates adaptive multiple-choice questions calibrated to your study material, reinforcing knowledge through targeted practice.',
  },
  {
    num: '03',
    title: 'Personalized Study Planning',
    desc: 'Produces day-by-day study schedules with spaced repetition built in, optimized for your available study time.',
  },
  {
    num: '04',
    title: 'Secure Document Processing',
    desc: 'Handles PDF uploads through a validated, sanitized pipeline that protects your data before any AI processing takes place.',
  },
  {
    num: '05',
    title: 'Multi-Agent Intelligence',
    desc: 'Coordinates specialized AI agents through a LangGraph workflow — each with a distinct academic role for consistent, high-quality outputs.',
  },
  {
    num: '06',
    title: 'Progress Tracking',
    desc: 'Monitors completed sessions and topic mastery over time so you can direct effort precisely where improvement is needed.',
  },
]

const STEPS = [
  {
    num: '1',
    title: 'Upload Study Material',
    desc: 'Submit your PDF or lecture notes through the secure document portal. All content is validated and sanitized before processing.',
  },
  {
    num: '2',
    title: 'AI Analyzes the Document',
    desc: 'A coordinated pipeline of specialized agents processes your material extracting key concepts, assessing difficulty, and structuring the content.',
  },
  {
    num: '3',
    title: 'Receive Your Learning Package',
    desc: 'Get a structured summary, adaptive practice questions, and a personalized multi-day study plan with spaced repetition built in.',
  },
]

export default function Landing() {
  const nav = useNavigate()

  return (
    <>
      {/* ── Navbar ─────────────────────────────────────────── */}
      <nav className="section-lp-nav">
        <div className="lp-nav-wrap">
          <div className="lp-nav-brand">AI Study Buddy</div>
          <div className="lp-nav-links">
            <span className="lp-nav-link">Features</span>
            <span className="lp-nav-link">How It Works</span>
          </div>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────── */}
      <section className="section-hero">
        <div className="hero-wrap">
          <span className="hero-badge">Powered by Multi-Agent AI</span>
          <h1 className="hero-title">
            Your Intelligent<br />
            <em>Academic Study</em><br />
            Companion
          </h1>
          <p className="hero-subtitle">
            Transform any study material into structured, adaptive learning experiences.
            AI-generated summaries, personalized study plans, and smart assessments
            — all in one academic platform.
          </p>
        </div>
        <div className="hero-cta-row">
          <button className="btn" onClick={() => nav('/login')}>
            Get Started
          </button>
        </div>
      </section>

      {/* ── Features ───────────────────────────────────────── */}
      <section className="section-features">
        <div className="features-wrap">
          <div className="features-heading">
            <span className="eyebrow">Capabilities</span>
            <h2>
              Everything You Need<br />
              to Study Smarter
            </h2>
            <p>
              A complete multi-agent AI system designed to accelerate learning and
              improve academic outcomes.
            </p>
          </div>
          <div className="feat-grid">
            {FEATURES.map((f) => (
              <div key={f.num} className="feat-card">
                <span className="feat-num">{f.num}</span>
                <h3 className="feat-title">{f.title}</h3>
                <p className="feat-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ───────────────────────────────────── */}
      <section className="section-how">
        <div className="how-wrap">
          <span className="eyebrow">Process</span>
          <h2>How It Works</h2>
          <div className="steps">
            {STEPS.map((s) => (
              <div key={s.num} className="step">
                <div className="step-num">{s.num}</div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Why ────────────────────────────────────────────── */}
      <section className="section-why">
        <div className="why-wrap">
          <div className="why-grid">
            <div className="why-left">
              <span className="eyebrow">Academic Value</span>
              <h2>Designed for Serious Learners</h2>
            </div>
            <div className="why-right">
              <p>
                AI Study Buddy applies established principles from cognitive science —
                spaced repetition, active recall, and deliberate practice — within a
                modern AI-driven workflow. Rather than replacing the effort of studying,
                it directs that effort more precisely.
              </p>
              <p>
                Built on a multi-agent LangGraph architecture with production-grade
                security, the system delivers consistent, reliable academic support at
                scale.
              </p>
              <div className="why-stats">
                <div className="stat">
                  <h3>3x</h3>
                  <p>Faster concept review with AI summarization</p>
                </div>
                <div className="stat">
                  <h3>3+</h3>
                  <p>Specialized AI agents working in coordination</p>
                </div>
                <div className="stat">
                  <h3>100%</h3>
                  <p>Input validated before any LLM invocation</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────────────────────── */}
      <section className="section-cta">
        <div className="cta-wrap">
          <h2>Begin Your Learning Journey</h2>
          <p>
            Join a platform built for academic excellence. Your study materials
            become structured, intelligent learning experiences.
          </p>
        </div>
        <div className="cta-btn-row">
          <button className="btn" onClick={() => nav('/login')}>
            Continue to Sign In
          </button>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────── */}
      <footer className="section-footer">
        <div className="footer-wrap">
          <span className="lp-footer-brand">AI Study Buddy</span>
          <span className="lp-footer-copy">
            Built with LangGraph · LangChain · Gemini 2.5 Flash
          </span>
        </div>
      </footer>
    </>
  )
}
