import { useEffect, useRef } from "react";
import { IconChat } from "./Icons";

export default function MessageList({ messages, loading }) {
  const bottomRef = useRef(null);

  // Auto scroll whenever messages or loading changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="messages messages-empty">
        <IconChat />
        <p>Select PDFs and ask a question about your documents.</p>
      </div>
    );
  }

  return (
    <div className="messages">
      {messages.map((m, i) => (
        <div key={i} className={`message ${m.role}`}>
          <div>
            <div className="message-label">
              {m.role === "user" ? "You" : "AI Assistant"}
            </div>
            <div className="message-bubble">{m.text}</div>
          </div>
        </div>
      ))}

      {loading && (
        <div className="message ai">
          <div className="message-bubble">
            <div className="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      )}

      {/* 👇 scroll anchor */}
      <div ref={bottomRef} />
    </div>
  );
}