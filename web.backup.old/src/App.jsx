import { useState, useEffect } from 'react'
import './App.css'
import Dashboard from './pages/Dashboard'
import AgentList from './components/AgentList'
import TaskMonitor from './components/TaskMonitor'
import StreamingResponse from './components/StreamingResponse'

function App() {
  const [agents, setAgents] = useState([])
  const [tasks, setTasks] = useState([])
  const [activeTab, setActiveTab] = useState('dashboard')
  const [streamingSession, setStreamingSession] = useState(null)

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:3000/agents')
      const data = await response.json()
      const transformedAgents = data.agentes.map(agent => ({
        id: agent.id,
        name: agent.nombre,
        role: agent.rol || 'Usuario',
        status: agent.estado === 'Inactivo' ? 'idle' : 'active',
        objetivo: agent.objetivo,
        progreso: agent.progreso,
        modelo: agent.modelo || 'glm4:9b'
      }))
      setAgents(transformedAgents)
    } catch (error) {
      console.error('Error cargando agentes:', error)
      // Fallback a mock data si falla
      const mockAgents = [
        { id: 'agent_1', name: 'Vendedor Bot', role: 'Sales', status: 'active', modelo: 'glm4:9b' },
        { id: 'agent_2', name: 'Analizador', role: 'Analyzer', status: 'idle', modelo: 'glm4:9b' },
      ]
      setAgents(mockAgents)
    }
  }

  useEffect(() => {
    fetchAgents()

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
        <h1>🚀 ELAP Dashboard v1.5.0</h1>
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
        {activeTab === 'agents' && (
          <AgentList
            agents={agents}
            onAgentCreated={fetchAgents}
            onStreamingStart={(agentId, query) => setStreamingSession({ agentId, query })}
          />
        )}
        {activeTab === 'tasks' && <TaskMonitor tasks={tasks} />}

        {streamingSession && (
          <StreamingResponse
            agentId={streamingSession.agentId}
            query={streamingSession.query}
            onClose={() => setStreamingSession(null)}
          />
        )}
      </main>

      <footer className="footer">
        <p>ELAP Enterprise Local AI Platform • v1.5.0</p>
      </footer>
    </div>
  )
}

export default App
