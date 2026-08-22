import { Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import DecisionResult from './pages/DecisionResult'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/result" element={<DecisionResult />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  )
}

export default App
