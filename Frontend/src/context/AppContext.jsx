import { createContext, useContext, useState } from 'react'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [user, setUser]             = useState(null)
  const [summaryData, setSummaryData] = useState(null)  // from /api/summarize
  const [quizData, setQuizData]     = useState(null)    // from /api/quiz
  const [planData, setPlanData]     = useState(null)    // from /api/study-plan

  return (
    <AppContext.Provider value={{
      user, setUser,
      summaryData, setSummaryData,
      quizData, setQuizData,
      planData, setPlanData,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  return useContext(AppContext)
}
