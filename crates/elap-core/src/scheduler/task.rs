//! Task definition and status tracking

use std::fmt;
use uuid::Uuid;

/// Unique task identifier
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct TaskId(Uuid);

impl TaskId {
    /// Create a new random task ID
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}

impl Default for TaskId {
    fn default() -> Self {
        Self::new()
    }
}

impl fmt::Display for TaskId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

/// Task priority level
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum TaskPriority {
    /// Low priority (background tasks)
    Low = 0,
    /// Normal priority (default)
    Normal = 1,
    /// High priority (user-facing)
    High = 2,
}

impl Default for TaskPriority {
    fn default() -> Self {
        TaskPriority::Normal
    }
}

/// Task execution status
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskStatus {
    /// Waiting in queue
    Pending,
    /// Currently executing
    Running,
    /// Completed successfully
    Completed,
    /// Failed with error
    Failed,
    /// Cancelled by user
    Cancelled,
}

impl fmt::Display for TaskStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TaskStatus::Pending => write!(f, "pending"),
            TaskStatus::Running => write!(f, "running"),
            TaskStatus::Completed => write!(f, "completed"),
            TaskStatus::Failed => write!(f, "failed"),
            TaskStatus::Cancelled => write!(f, "cancelled"),
        }
    }
}

/// A task to be executed
#[derive(Debug, Clone)]
pub struct Task {
    /// Unique identifier
    pub id: TaskId,
    /// Task name for logging
    pub name: String,
    /// Priority level
    pub priority: TaskPriority,
    /// Current status
    pub status: TaskStatus,
    /// Creation timestamp
    pub created_at: chrono::DateTime<chrono::Utc>,
    /// Last status update
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

impl Task {
    /// Create a new task
    pub fn new(name: impl Into<String>) -> Self {
        let now = chrono::Utc::now();
        Self {
            id: TaskId::new(),
            name: name.into(),
            priority: TaskPriority::default(),
            status: TaskStatus::Pending,
            created_at: now,
            updated_at: now,
        }
    }

    /// Set task priority
    pub fn with_priority(mut self, priority: TaskPriority) -> Self {
        self.priority = priority;
        self
    }

    /// Update status
    pub fn set_status(&mut self, status: TaskStatus) {
        self.status = status;
        self.updated_at = chrono::Utc::now();
    }

    /// Get time elapsed since creation
    pub fn elapsed(&self) -> chrono::Duration {
        chrono::Utc::now() - self.created_at
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_task_creation() {
        let task = Task::new("test_task");
        assert_eq!(task.name, "test_task");
        assert_eq!(task.status, TaskStatus::Pending);
        assert_eq!(task.priority, TaskPriority::Normal);
    }

    #[test]
    fn test_task_with_priority() {
        let task = Task::new("high_priority").with_priority(TaskPriority::High);
        assert_eq!(task.priority, TaskPriority::High);
    }

    #[test]
    fn test_task_status_update() {
        let mut task = Task::new("test");
        task.set_status(TaskStatus::Running);
        assert_eq!(task.status, TaskStatus::Running);
    }

    #[test]
    fn test_task_id_unique() {
        let task1 = Task::new("task1");
        let task2 = Task::new("task2");
        assert_ne!(task1.id, task2.id);
    }

    #[test]
    fn test_task_elapsed() {
        let task = Task::new("test");
        std::thread::sleep(std::time::Duration::from_millis(10));
        assert!(task.elapsed().num_milliseconds() >= 10);
    }
}
