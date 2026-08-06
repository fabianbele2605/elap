import React from 'react'
import '../styles/Dashboard.css'

export default function Dashboard({ agents, tasks }) {
  const activeAgents = agents.filter(a => a.status === 'active').length
  const completedTasks = tasks.filter(t => t.status === 'completed').length

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Active Agents</h3>
          <p className="stat-value">{activeAgents}/{agents.length}</p>
        </div>
        <div className="stat-card">
          <h3>Tasks Completed</h3>
          <p className="stat-value">{completedTasks}/{tasks.length}</p>
        </div>
        <div className="stat-card">
          <h3>System Status</h3>
          <p className="stat-value">✅ Healthy</p>
        </div>
        <div className="stat-card">
          <h3>Uptime</h3>
          <p className="stat-value">99.9%</p>
        </div>
      </div>

      <div className="recent-section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          {tasks.slice(0, 5).map(task => (
            <div key={task.id} className="activity-item">
              <span>{task.description}</span>
              <span className={`status ${task.status}`}>{task.status}</span>
              <div className="progress-bar">
                <div className="progress" style={{ width: `${task.progress}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
