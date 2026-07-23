import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function validate(name, email, pw, pw2) {
  const errs = []
  if (!name || !name.trim())    errs.push('Full name is required.')
  if (!email || !email.includes('@')) errs.push('A valid email address is required.')
  if (!pw || pw.length < 8)    errs.push('Password must be at least 8 characters.')
  if (pw !== pw2)               errs.push('Passwords do not match.')
  return errs
}

export default function Signup() {
  const nav = useNavigate()

  const [name, setName]       = useState('')
  const [email, setEmail]     = useState('')
  const [pw, setPw]           = useState('')
  const [pw2, setPw2]         = useState('')
  const [errors, setErrors]   = useState([])
  const [success, setSuccess] = useState(false)

  function handleSubmit(e) {
    e.preventDefault()
    const errs = validate(name, email, pw, pw2)
    if (errs.length > 0) {
      setErrors(errs)
      setSuccess(false)
      return
    }
    setErrors([])
    setSuccess(true)
    setTimeout(() => nav('/login'), 1200)
  }

  return (
    <>
      <nav className="auth-nav">
        <span className="auth-nav-brand">AI Study Buddy</span>
      </nav>

      <div className="auth-page">
        <div className="auth-box">
          <div className="auth-head">
            <h1>Create Account</h1>
            <p>Start your personalized academic learning experience</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {errors.map((err, i) => (
              <div key={i} className="alert alert-error">
                {err}
              </div>
            ))}
            {success && (
              <div className="alert alert-success">
                Account created. Redirecting to sign in…
              </div>
            )}

            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                id="name"
                type="text"
                placeholder="Your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
              />
            </div>

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
              <label htmlFor="pw">Password</label>
              <input
                id="pw"
                type="password"
                placeholder="Minimum 8 characters"
                value={pw}
                onChange={(e) => setPw(e.target.value)}
                autoComplete="new-password"
              />
            </div>

            <div className="form-group">
              <label htmlFor="pw2">Confirm Password</label>
              <input
                id="pw2"
                type="password"
                placeholder="Repeat your password"
                value={pw2}
                onChange={(e) => setPw2(e.target.value)}
                autoComplete="new-password"
              />
            </div>

            <button type="submit" className="btn btn-full" style={{ marginTop: '8px' }}>
              Create Account
            </button>
          </form>

          <div className="auth-divider">Already have an account?</div>

          <button className="btn btn-full" onClick={() => nav('/login')}>
            Sign In to Existing Account
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
