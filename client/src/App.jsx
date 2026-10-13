import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import useGetCurrentUser from './hooks/useGetCurrentUser'
export const serverUrl = "http://localhost:8000"

function App() {
  useGetCurrentUser()
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
