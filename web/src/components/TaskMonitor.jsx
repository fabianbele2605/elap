import React from 'react'
import '../styles/TaskMonitor.css'

export default function TaskMonitor({ tasks }) {
  return (
    <div className="task-monitor">
      <h2>Tasks</h2>
      <div className="tasks-grid">
        {tasks.map(task => (
          <div key={task.id} className="task-card">
            <h3>{task.description}</h3>
            <div className="task-info">
              <span className={`badge ${task.status}`}>{task.status}</span>
              <span className="progress-text">{task.progress}%</span>
            </div>
            <div className="progress-bar">
              <div className="progress" style={{ width: `${task.progress}%` }}></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
