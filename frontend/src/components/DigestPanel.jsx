function DigestPanel({ digest, onRefresh, refreshing }) {
  return (
    <section className="panel digest-panel">
      <div className="panel-header">
        <h2>Daily Digest</h2>
        <button type="button" onClick={onRefresh} disabled={refreshing}>
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <p className="digest-summary">{digest?.summary || "No digest loaded yet."}</p>

      <div className="digest-metrics">
        <div className="metric-card">
          <strong>{digest?.tasks_count ?? 0}</strong>
          <span>Tasks</span>
        </div>
        <div className="metric-card">
          <strong>{digest?.events_count ?? 0}</strong>
          <span>Events</span>
        </div>
        <div className="metric-card">
          <strong>{digest?.reminders_count ?? 0}</strong>
          <span>Reminders</span>
        </div>
      </div>

      <div className="digest-list-grid">
        <div>
          <h3>Top Tasks</h3>
          <ul>
            {(digest?.tasks || []).map((task, index) => (
              <li key={`${task.title}-${index}`}>
                {task.title}
                <span>{task.priority}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3>Top Events</h3>
          <ul>
            {(digest?.events || []).map((event, index) => (
              <li key={`${event.title}-${index}`}>
                {event.title}
                <span>{new Date(event.start_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default DigestPanel;
