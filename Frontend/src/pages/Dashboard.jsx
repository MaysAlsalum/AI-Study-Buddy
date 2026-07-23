import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'

export default function Dashboard() {
  const nav = useNavigate()
  const { setSummaryData, setUser } = useApp()

  const [file, setFile]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [error, setError]     = useState(null)
  const inputRef = useRef(null)

  function handleFile(f) {
    if (f && f.type === 'application/pdf') {
      setFile(f)
      setError(null)
    } else if (f) {
      setError('Only PDF files are accepted.')
    }
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  async function handleSummarize() {
    if (!file || loading) return
    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch('/api/summarize', { method: 'POST', body: formData })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        setError(err.detail || `Server error (${res.status}).`)
        return
      }

      const data = await res.json()
      setSummaryData(data)
      nav('/summary')
    } catch {
      setError('Could not reach the backend. Make sure the server is running on port 8080.')
    } finally {
      setLoading(false)
    }
  }

  function handleSignOut() {
    setUser(null)
    nav('/')
  }

  return (
    <>
      <nav className="app-nav">
        <div className="app-nav-inner">
          <span className="app-nav-brand">AI Study Buddy</span>
          <span className="app-nav-file">Dashboard</span>
        </div>
      </nav>

      <div className="dash-hero">
        <h1>Upload a Study Document</h1>
        <p>
          Upload your PDF and the AI will extract a summary, key topics,
          and definitions — then you can generate a quiz or study plan.
        </p>
      </div>

      <div className="dash-body">
        <div className="dash-upload-wrap">
          <div className="dash-card">
            <span className="card-eyebrow">Step 1 — Study Document</span>
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
                <span className="file-chip-size">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            )}
          </div>
        </div>

        <div className="dash-actions">
          <button
            className="btn"
            style={{ minWidth: 240 }}
            disabled={!file || loading}
            onClick={handleSummarize}
          >
            {loading ? (
              <><span className="spinner" />Analyzing document…</>
            ) : (
              'Summarize Document'
            )}
          </button>

          {!file && <p className="dash-hint">Upload a PDF file to get started.</p>}

          {error && (
            <p className="dash-hint" style={{ color: '#DC2626' }}>{error}</p>
          )}

          {loading && (
            <div className="processing-overlay">
              <div className="processing-spinner" />
              Extracting summary, topics, and definitions…
            </div>
          )}
        </div>

        <div className="dash-signout">
          <button className="btn btn-sm" onClick={handleSignOut}>Sign Out</button>
        </div>
      </div>
    </>
  )
}
