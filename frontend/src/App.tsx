import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import WorldView from './pages/WorldView'
import EntityInspector from './pages/EntityInspector'
import SystemControl from './pages/SystemControl'
import StatsDashboard from './pages/StatsDashboard'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<WorldView />} />
          <Route path="entities" element={<EntityInspector />} />
          <Route path="systems" element={<SystemControl />} />
          <Route path="stats" element={<StatsDashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
