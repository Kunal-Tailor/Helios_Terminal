import { Route, Routes } from 'react-router-dom'
import Home from './pages/Home'
import DecisionResult from './pages/DecisionResult'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/result" element={<DecisionResult />} />
    </Routes>
  )
}

export default App
