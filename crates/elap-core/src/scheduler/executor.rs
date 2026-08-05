//! Task scheduler and executor

use super::queue::TaskQueue;
use super::task::{Task, TaskId, TaskPriority};
use tokio::sync::Mutex;
use std::sync::Arc;

/// Main task scheduler
///
/// Manages task execution with Tokio runtime.
/// Handles enqueueing, dequeuing, and tracking task status.
pub struct TaskScheduler {
    queue: Arc<Mutex<TaskQueue>>,
    max_concurrent: usize,
}

impl TaskScheduler {
    /// Create a new task scheduler
    pub fn new(max_concurrent: usize) -> Self {
        Self {
            queue: Arc::new(Mutex::new(TaskQueue::new(max_concurrent))),
            max_concurrent,
        }
    }

    /// Submit a task to the queue
    pub async fn submit_task(&self, task: Task) -> TaskId {
        let mut queue = self.queue.lock().await;
        queue.enqueue(task)
    }

    /// Submit a simple named task
    pub async fn submit(&self, name: impl Into<String>) -> TaskId {
        self.submit_task(Task::new(name)).await
    }

    /// Submit a high-priority task
    pub async fn submit_high_priority(&self, name: impl Into<String>) -> TaskId {
        let task = Task::new(name).with_priority(TaskPriority::High);
        self.submit_task(task).await
    }

    /// Get task status
    pub async fn get_task_status(&self, task_id: TaskId) -> Option<String> {
        let queue = self.queue.lock().await;
        queue.get_task(task_id).map(|t| t.status.to_string())
    }

    /// Mark task as completed
    pub async fn complete_task(&self, task_id: TaskId) {
        let mut queue = self.queue.lock().await;
        queue.mark_completed(task_id);
    }

    /// Mark task as failed
    pub async fn fail_task(&self, task_id: TaskId) {
        let mut queue = self.queue.lock().await;
        queue.mark_failed(task_id);
    }

    /// Get queue statistics
    pub async fn stats(&self) -> TaskSchedulerStats {
        let queue = self.queue.lock().await;
        TaskSchedulerStats {
            pending: queue.pending_count(),
            running: queue.running_count(),
            total: queue.total_count(),
            max_concurrent: self.max_concurrent,
        }
    }

    /// Get next task to execute
    pub async fn next_task(&self) -> Option<Task> {
        let mut queue = self.queue.lock().await;
        queue.dequeue()
    }
}

/// Scheduler statistics
#[derive(Debug, Clone)]
pub struct TaskSchedulerStats {
    /// Pending tasks in queue
    pub pending: usize,
    /// Currently running tasks
    pub running: usize,
    /// Total tasks managed
    pub total: usize,
    /// Maximum concurrent tasks allowed
    pub max_concurrent: usize,
}

impl std::fmt::Display for TaskSchedulerStats {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Tasks - Pending: {}, Running: {}/{}, Total: {}",
            self.pending, self.running, self.max_concurrent, self.total
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_scheduler_creation() {
        let scheduler = TaskScheduler::new(4);
        let stats = scheduler.stats().await;
        assert_eq!(stats.pending, 0);
        assert_eq!(stats.running, 0);
        assert_eq!(stats.max_concurrent, 4);
    }

    #[tokio::test]
    async fn test_submit_task() {
        let scheduler = TaskScheduler::new(4);
        let task_id = scheduler.submit("test_task").await;
        
        let stats = scheduler.stats().await;
        assert_eq!(stats.total, 1);
    }

    #[tokio::test]
    async fn test_next_task() {
        let scheduler = TaskScheduler::new(4);
        scheduler.submit("task1").await;
        
        let task = scheduler.next_task().await;
        assert!(task.is_some());
        
        let stats = scheduler.stats().await;
        assert_eq!(stats.pending, 0);
        assert_eq!(stats.running, 1);
    }

    #[tokio::test]
    async fn test_complete_task() {
        let scheduler = TaskScheduler::new(4);
        let id = scheduler.submit("task").await;
        
        scheduler.next_task().await;
        scheduler.complete_task(id).await;
        
        let stats = scheduler.stats().await;
        assert_eq!(stats.running, 0);
    }

    #[tokio::test]
    async fn test_high_priority() {
        let scheduler = TaskScheduler::new(100);
        
        scheduler.submit("low").await;
        let high_id = scheduler.submit_high_priority("high").await;
        scheduler.submit("normal").await;
        
        let first = scheduler.next_task().await.unwrap();
        assert_eq!(first.id, high_id);
    }
}
