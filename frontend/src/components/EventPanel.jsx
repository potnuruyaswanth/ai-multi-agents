function EventPanel({ events }) {
  return (
    <section className="panel">
      <h2>Events</h2>
      {events.length === 0 ? <p>No events yet.</p> : null}
      <ul>
        {events.map((event) => (
          <li key={event.event_id}>
            <strong>{event.title}</strong>
            <div>Type: {event.type}</div>
            <div>Start: {new Date(event.start_at).toLocaleString()}</div>
            <div>End: {new Date(event.end_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default EventPanel;
