import { useEffect, useState } from "react";
import IntegrationPanel from "../components/IntegrationPanel";
import DigestPanel from "../components/DigestPanel";
import ChatPanel from "../components/ChatPanel";
import EventPanel from "../components/EventPanel";
import DriveAssetsPanel from "../components/DriveAssetsPanel";
import TaskPanel from "../components/TaskPanel";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

function DashboardPage() {
  const [tasks, setTasks] = useState([]);
  const [events, setEvents] = useState([]);
  const [googleStatus, setGoogleStatus] = useState({ gmail: null, calendar: null, tasks: null });
  const [digest, setDigest] = useState(null);
  const [driveAssets, setDriveAssets] = useState([]);
  const [status, setStatus] = useState("Not connected");
  const [syncing, setSyncing] = useState(false);

  const loadData = async () => {
    const [tasksRes, eventsRes] = await Promise.all([
      fetch(`${API_BASE}/tasks`),
      fetch(`${API_BASE}/events`)
    ]);

    const tasksData = await tasksRes.json();
    const eventsData = await eventsRes.json();

    setTasks(tasksData.tasks || []);
    setEvents(eventsData.events || []);

    const statusRes = await fetch(`${API_BASE}/google/status?user_id=default-user`);
    const statusData = await statusRes.json();
    setGoogleStatus(statusData);

    const digestRes = await fetch(`${API_BASE}/daily-digest?user_email=student@example.com&user_id=default-user`);
    const digestData = await digestRes.json();
    setDigest(digestData);

    const driveRes = await fetch(`${API_BASE}/google/drive/resources?user_id=default-user`);
    const driveData = await driveRes.json();
    setDriveAssets(driveData.resources || []);
  };

  useEffect(() => {
    loadData();
  }, []);

  const askChat = async (message) => {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    return data.reply || "No response from assistant.";
  };

  const connectProvider = async (provider) => {
    const response = await fetch(`${API_BASE}/auth/google/${provider}/url?user_id=default-user`);
    const data = await response.json();
    if (data.authorization_url) {
      window.open(data.authorization_url, "_blank", "noopener,noreferrer");
      setStatus(`Opened ${provider} OAuth flow`);
    }
  };

  const syncGmail = async () => {
    setSyncing(true);
    setStatus("Syncing Gmail inbox...");
    try {
      const response = await fetch(`${API_BASE}/google/gmail/sync?user_id=default-user`, { method: "POST" });
      const data = await response.json();
      setStatus(`Synced ${data.count || 0} Gmail message(s)`);
      await loadData();
    } finally {
      setSyncing(false);
    }
  };

  const syncCalendar = async () => {
    setSyncing(true);
    setStatus("Syncing calendar events...");
    try {
      const now = new Date();
      const end = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000);
      const response = await fetch(
        `${API_BASE}/google/calendar/events?user_id=default-user&start_iso=${encodeURIComponent(now.toISOString())}&end_iso=${encodeURIComponent(end.toISOString())}`
      );
      const data = await response.json();
      setStatus(`Loaded ${data.events?.length || 0} Google Calendar event(s)`);
      await loadData();
    } finally {
      setSyncing(false);
    }
  };

  const syncTasks = async () => {
    setSyncing(true);
    setStatus("Syncing tasks to Google Tasks...");
    try {
      const response = await fetch(`${API_BASE}/google/tasks/sync?user_id=default-user`, { method: "POST" });
      const data = await response.json();
      setStatus(`Synced ${data.synced || 0} task(s)`);
      await loadData();
    } finally {
      setSyncing(false);
    }
  };

  const refreshDigest = async () => {
    setSyncing(true);
    try {
      const digestRes = await fetch(`${API_BASE}/daily-digest?user_email=student@example.com&user_id=default-user`);
      const digestData = await digestRes.json();
      setDigest(digestData);
    } finally {
      setSyncing(false);
    }
  };

  const refreshDriveAssets = async () => {
    setSyncing(true);
    try {
      const response = await fetch(`${API_BASE}/google/drive/resources?user_id=default-user`);
      const data = await response.json();
      setDriveAssets(data.resources || []);
      setStatus(`Loaded ${data.resources?.length || 0} Drive resource(s)`);
    } finally {
      setSyncing(false);
    }
  };

  const runReminders = async () => {
    setSyncing(true);
    setStatus("Running reminder scan...");
    try {
      const response = await fetch(`${API_BASE}/google/reminders/run?user_email=student@example.com&hours_ahead=24`, {
        method: "POST"
      });
      const data = await response.json();
      setStatus(`Created ${data.count || 0} reminder notification(s)`);
      await loadData();
    } finally {
      setSyncing(false);
    }
  };

  return (
    <main className="dashboard">
      <header>
        <h1>AI Productivity Assistant</h1>
        <p>Automated tasks, schedules, and reminders powered by multi-agent orchestration.</p>
      </header>

      <IntegrationPanel
        status={status}
        googleStatus={googleStatus}
        syncing={syncing}
        onConnectGmail={() => connectProvider("gmail")}
        onConnectCalendar={() => connectProvider("calendar")}
        onConnectTasks={() => connectProvider("tasks")}
        onConnectDrive={() => connectProvider("drive")}
        onSyncGmail={syncGmail}
        onSyncCalendar={syncCalendar}
        onSyncTasks={syncTasks}
        onRunReminders={runReminders}
      />

      <DigestPanel digest={digest} onRefresh={refreshDigest} refreshing={syncing} />

      <DriveAssetsPanel assets={driveAssets} status={googleStatus?.drive?.connected ? "Connected" : "Not connected"} />

      <div className="panel action-panel">
        <button type="button" onClick={refreshDriveAssets} disabled={syncing}>Refresh Drive Assets</button>
      </div>

      <div className="grid">
        <TaskPanel tasks={tasks} />
        <EventPanel events={events} />
      </div>

      <ChatPanel onSend={askChat} />
    </main>
  );
}

export default DashboardPage;
