import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import useGetCurrentUser from './hooks/useGetCurrentUser'
import { useSelector } from 'react-redux'
import Dashboard from './pages/Dashboard'
import Generate from './pages/Generate'
import WebsiteEditor from './pages/Editor'
import LiveSite from './pages/LiveSite'
export const serverUrl = "http://localhost:8000"

function App() {
  useGetCurrentUser()
  const { userData } = useSelector(state => state.user)
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={userData ? <Dashboard /> : <Home />} />
        <Route path="/generate" element={userData ? <Generate /> : <Home />} />
        <Route path="/editor/:id" element={userData ? <WebsiteEditor /> : <Home />} />
        <Route path="/site/:id" element={<LiveSite />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
