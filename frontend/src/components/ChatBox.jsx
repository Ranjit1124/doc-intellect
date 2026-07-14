import { chat } from "../api/api";
import MessageList from "./MessageList";
import { IconSend } from "./Icons";

export default function ChatBox({ selectedFiles, messages, setMessages, question, setQuestion, loading, setLoading }) {

  const send = async () => {
    if (!question.trim() || loading) return;

    if (selectedFiles.length === 0) {
      alert("Select at least one PDF from the document library.");
      return;
    }

    const text = question.trim();
    const updated = [...messages, { role: "user", text }];

    setMessages(updated);
    setQuestion("");
    setLoading(true);

    // 1. Add an empty AI placeholder message to the chat array that we can stream text into
    const aiMessageIndex = updated.length;
    setMessages([...updated, { role: "ai", text: "" }]);

    try {
      const res = await chat(text, selectedFiles);

      // 2. Setup the stream reader and text decoder
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let isDone = false;
      let accumulatedText = "";

      // 3. Read the pipeline data piece by piece
      while (!isDone) {
        const { value, done } = await reader.read();
        isDone = done;
        
        const chunk = decoder.decode(value, { stream: !isDone });
        accumulatedText += chunk;

        // 4. Update the placeholder AI message continuously as words arrive
        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          updatedMessages[aiMessageIndex] = { role: "ai", text: accumulatedText };
          return updatedMessages;
        });
      }

    } catch (err) {
      // Handle fallback errors gracefully if the stream snaps
      setMessages((prevMessages) => {
        const updatedMessages = [...prevMessages];
        if (updatedMessages[aiMessageIndex]) {
          updatedMessages[aiMessageIndex] = { 
            role: "ai", 
            text: err.message || "Chat request failed." 
          };
        }
        return updatedMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="card chat-card">
      <div className="card-header">
        <h2>AI Chat</h2>
        <span className="badge badge-info">
          {selectedFiles.length} PDF{selectedFiles.length !== 1 ? "s" : ""} selected
        </span>
      </div>

      {selectedFiles.length > 0 && (
        <div className="chat-selected">
          {selectedFiles.map((f) => (
            <span key={f} className="chat-tag" title={f}>
              {f}
            </span>
          ))}
        </div>
      )}

      <div className="chat-body">
        <MessageList messages={messages} loading={loading} />

        <div className="chat-input-row">
          <input
            type="text"
            placeholder="Ask a question about your PDFs..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            type="button"
            className="btn btn-primary"
            onClick={send}
            disabled={loading || !question.trim()}
          >
            <IconSend />
            Send
          </button>
        </div>
      </div>
    </div>
  );
}