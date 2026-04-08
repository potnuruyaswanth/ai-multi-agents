import { useState } from "react";

function ChatPanel({ onSend }) {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    setLoading(true);
    const result = await onSend(message);
    setReply(result);
    setLoading(false);
  };

  return (
    <section className="panel chat-panel">
      <h2>Assistant Chat</h2>
      <form onSubmit={submit}>
        <input
          placeholder="Ask: what are my tasks tomorrow?"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>
      <div className="reply-box">{reply || "Response appears here."}</div>
    </section>
  );
}

export default ChatPanel;
