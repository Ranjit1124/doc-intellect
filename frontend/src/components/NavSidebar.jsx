import { IconDocuments, IconChat } from "./Icons";

export default function NavSidebar({ activeView, setActiveView, fileCount, selectedCount }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">P</div>
        <div className="sidebar-brand-text">
          <h1>PDF Chat</h1>
          <p>Document AI Assistant</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <button
          type="button"
          className={`nav-item ${activeView === "documents" ? "active" : ""}`}
          onClick={() => setActiveView("documents")}
        >
          <IconDocuments />
          <span>Documents</span>
        </button>
        <button
          type="button"
          className={`nav-item ${activeView === "chat" ? "active" : ""}`}
          onClick={() => setActiveView("chat")}
        >
          <IconChat />
          <span>AI Chat</span>
        </button>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-stat">
          <div className="sidebar-stat-label">Total PDFs</div>
          <div className="sidebar-stat-value">{fileCount}</div>
        </div>
        {selectedCount > 0 && (
          <div className="sidebar-stat" style={{ marginTop: 10 }}>
            <div className="sidebar-stat-label">Selected</div>
            <div className="sidebar-stat-value">{selectedCount}</div>
          </div>
        )}
      </div>
    </aside>
  );
}
