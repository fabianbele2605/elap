import React from 'react'
import '../styles/AgentList.css'

export default function AgentList({ agents }) {
  return (
    <div className="agent-list">
      <h2>Agents</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Role</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {agents.map(agent => (
            <tr key={agent.id}>
              <td>{agent.id}</td>
              <td>{agent.name}</td>
              <td>{agent.role}</td>
              <td>
                <span className={`badge ${agent.status}`}>
                  {agent.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
