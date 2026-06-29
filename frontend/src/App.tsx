import { useEffect, useState } from 'react'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Analytics from './pages/Analytics'
import Candidates from './pages/Candidates'
import Dashboard from './pages/Dashboard'
import Matching from './pages/Matching'
import AllResumes from './pages/AllResumes'
import JDAnalyzer from './pages/JDAnalyzer'

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' || 'light'
    setTheme(savedTheme)
    document.documentElement.classList.toggle('dark', savedTheme === 'dark')
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark', newTheme === 'dark')
  }

  return (
    <Router>
      <Layout theme={theme} toggleTheme={toggleTheme}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/candidates" element={<Candidates />} />
          <Route path="/all-resumes" element={<AllResumes />} />
          <Route path="/matching" element={<Matching />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/jd-analyzer" element={<JDAnalyzer />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
