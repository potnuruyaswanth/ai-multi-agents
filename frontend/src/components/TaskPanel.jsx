function TaskPanel({ tasks }) {
  return (
    <section className="panel">
      <h2>Tasks</h2>
      {tasks.length === 0 ? <p>No tasks yet.</p> : null}
      <ul>
        {tasks.map((task) => (
          <li key={task.task_id}>
            <strong>{task.title}</strong>
            <div>Status: {task.status}</div>
            <div>Priority: {task.priority}</div>
            <div>Due: {task.due_at ? new Date(task.due_at).toLocaleString() : "N/A"}</div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default TaskPanel;
