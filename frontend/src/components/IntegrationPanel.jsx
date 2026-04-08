function IntegrationPanel({ status, googleStatus, onConnectGmail, onConnectCalendar, onConnectTasks, onConnectDrive, onSyncGmail, onSyncCalendar, onSyncTasks, onRunReminders, syncing }) {
  return (
    <section className="panel integration-panel">
      <h2>Google Integrations</h2>
      <p>Connect your Gmail and Calendar accounts, then sync new messages and events into the assistant.</p>

      <div className="integration-actions">
        <button type="button" onClick={onConnectGmail}>Connect Gmail</button>
        <button type="button" onClick={onConnectCalendar}>Connect Calendar</button>
        <button type="button" onClick={onConnectTasks}>Connect Tasks</button>
        <button type="button" onClick={onConnectDrive}>Connect Drive</button>
        <button type="button" onClick={onSyncGmail} disabled={syncing}>Sync Gmail Inbox</button>
        <button type="button" onClick={onSyncCalendar} disabled={syncing}>Sync Calendar</button>
        <button type="button" onClick={onSyncTasks} disabled={syncing}>Sync Tasks</button>
        <button type="button" onClick={onRunReminders} disabled={syncing}>Run Reminder Scan</button>
      </div>

      <div className="integration-status">
        <strong>Status:</strong>
        <span>{status}</span>
      </div>

      <div className="integration-connection-grid">
        <div className="connection-card">
          <strong>Gmail</strong>
          <span>{googleStatus?.gmail?.connected ? `Connected: ${googleStatus.gmail.account_email || "account linked"}` : "Not connected"}</span>
        </div>
        <div className="connection-card">
          <strong>Calendar</strong>
          <span>{googleStatus?.calendar?.connected ? `Connected: ${googleStatus.calendar.account_email || "account linked"}` : "Not connected"}</span>
        </div>
        <div className="connection-card">
          <strong>Tasks</strong>
          <span>{googleStatus?.tasks?.connected ? `Connected: ${googleStatus.tasks.account_email || "account linked"}` : "Not connected"}</span>
        </div>
        <div className="connection-card">
          <strong>Drive</strong>
          <span>{googleStatus?.drive?.connected ? `Connected: ${googleStatus.drive.account_email || "account linked"}` : "Not connected"}</span>
        </div>
      </div>
    </section>
  );
}

export default IntegrationPanel;
