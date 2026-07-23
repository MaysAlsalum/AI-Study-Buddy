import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../context/AppContext.jsx'

export default function Login() {
  const nav = useNavigate()
  const { setUser } = useApp()

  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (!email || !password) {
      setError('Please enter your email and password.')
      return
    }
    setError('')
    setUser({ email })
    nav('/dashboard')
  }

  return (
    <>
      <nav className="auth-nav">
        <span className="auth-nav-brand">AI Study Buddy</span>
      </nav>

      <div className="auth-page">
        <div className="auth-box">
          <div className="auth-head">
            <h1>Sign In</h1>
            <p>Continue your academic learning journey</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                placeholder="you@university.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="Your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>

            <button type="submit" className="btn btn-full" style={{ marginTop: '8px' }}>
              Sign In
            </button>
          </form>

          <div className="auth-divider">Don't have an account?</div>

          <button className="btn btn-full" onClick={() => nav('/signup')}>
            Create an Account
          </button>

          <div className="auth-back">
            <button className="btn" onClick={() => nav('/')}>
              Back to Home
            </button>
          </div>
        </div>
      </div>
    </>
  )
}
