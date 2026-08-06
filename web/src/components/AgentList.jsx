import React, { useState } from 'react'
import '../styles/AgentList.css'

const AGENT_ROLES = [
  'Sales',
  'HR',
  'Accounting',
  'IT',
  'Legal',
  'Support',
  'Analytics',
  'Custom'
]

export default function AgentList({ agents, onAgentCreated }) {
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    nombre: '',
    rol: 'Sales',
    objetivo: ''
  })
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await fetch('http://localhost:3000/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        setFormData({ nombre: '', rol: 'Sales', objetivo: '' })
        setShowForm(false)
        onAgentCreated()
      } else {
        alert('Error creating agent')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error creating agent')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="agent-list">
      <div className="agents-header">
        <h2>Agents</h2>
        <button
          className="btn-create"
          onClick={() => setShowForm(!showForm)}
        >
          {showForm ? 'Cancel' : '+ New Agent'}
        </button>
      </div>

      {showForm && (
        <form className="agent-form" onSubmit={handleSubmit}>
          <input
            type="text"
            name="nombre"
            placeholder="Agent Name"
            value={formData.nombre}
            onChange={handleInputChange}
            required
          />
          <select
            name="rol"
            value={formData.rol}
            onChange={handleInputChange}
          >
            {AGENT_ROLES.map(role => (
              <option key={role} value={role}>{role}</option>
            ))}
          </select>
          <input
            type="text"
            name="objetivo"
            placeholder="Objective"
            value={formData.objetivo}
            onChange={handleInputChange}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Agent'}
          </button>
        </form>
      )}

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Role</th>
            <th>Status</th>
            <th>Model</th>
          </tr>
        </thead>
        <tbody>
          {agents.map(agent => (
            <tr key={agent.id}>
              <td title={agent.id}>{agent.id.slice(0, 8)}...</td>
              <td>{agent.name}</td>
              <td>{agent.role}</td>
              <td>
                <span className={`badge ${agent.status}`}>
                  {agent.status}
                </span>
              </td>
              <td className="model-cell">
                <code>{agent.modelo || 'glm4:9b'}</code>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
