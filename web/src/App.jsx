import { useState, useEffect } from 'react'
import './App.css'
import Dashboard from './pages/Dashboard'
import AgentList from './components/AgentList'
import TaskMonitor from './components/TaskMonitor'

function App() {
  const [agents, setAgents] = useState([])
  const [tasks, setTasks] = useState([])
  const [activeTab, setActiveTab] = useState('dashboard')

  useEffect(() => {
    // Simulación: cargar agentes
    const mockAgents = [
      { id: 'agent_1', name: 'Vendedor Bot', role: 'Sales', status: 'active' },
      { id: 'agent_2', name: 'Analizador', role: 'Analyzer', status: 'idle' },
      { id: 'agent_3', name: 'Validador', role: 'Validator', status: 'active' },
    ]
    setAgents(mockAgents)

    // Simulación: cargar tareas
    const mockTasks = [
      { id: 'task_1', description: 'Procesar pedidos', status: 'running', progress: 65 },
      { id: 'task_2', description: 'Validar datos', status: 'completed', progress: 100 },
      { id: 'task_3', description: 'Generar reporte', status: 'pending', progress: 0 },
    ]
    setTasks(mockTasks)
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>🚀 ELAP Dashboard v1.2.0</h1>
        <nav className="nav">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={activeTab === 'agents' ? 'active' : ''}
            onClick={() => setActiveTab('agents')}
          >
            Agents
          </button>
          <button
            className={activeTab === 'tasks' ? 'active' : ''}
            onClick={() => setActiveTab('tasks')}
          >
            Tasks
          </button>
        </nav>
      </header>

      <main className="main">
        {activeTab === 'dashboard' && <Dashboard agents={agents} tasks={tasks} />}
        {activeTab === 'agents' && <AgentList agents={agents} />}
        {activeTab === 'tasks' && <TaskMonitor tasks={tasks} />}
      </main>

      <footer className="footer">
        <p>ELAP Enterprise Local AI Platform • v1.2.0</p>
      </footer>
    </div>
  )
}

export default App
