import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppProvider } from './context/AppContext.jsx'
import Landing       from './pages/Landing.jsx'
import Login         from './pages/Login.jsx'
import Signup        from './pages/Signup.jsx'
import Dashboard     from './pages/Dashboard.jsx'
import SummaryPage   from './pages/SummaryPage.jsx'
import QuizPage      from './pages/QuizPage.jsx'
import StudyPlanPage from './pages/StudyPlanPage.jsx'

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"           element={<Landing />} />
          <Route path="/login"      element={<Login />} />
          <Route path="/signup"     element={<Signup />} />
          <Route path="/dashboard"  element={<Dashboard />} />
          <Route path="/summary"    element={<SummaryPage />} />
          <Route path="/quiz"       element={<QuizPage />} />
          <Route path="/study-plan" element={<StudyPlanPage />} />
          <Route path="*"           element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  )
}
