import { useState } from "react";

export default function Sidebar({
  files = [], // ✅ default fallback
  selectedFiles = [],
  setSelectedFiles,
  onDelete,
  onUploadClick
}) {

  const [search, setSearch] = useState("");

  const toggle = (file) => {
    if (selectedFiles.includes(file)) {
      setSelectedFiles(selectedFiles.filter(f => f !== file));
    } else {
      setSelectedFiles([...selectedFiles, file]);
    }
  };

  // 🔍 filter files (optional but useful for dashboard UX)
  const filteredFiles = Array.isArray(files)
    ? files.filter(f => f.toLowerCase().includes(search.toLowerCase()))
    : [];

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        padding: 15,
        background: "#f8f9fb",
        borderRight: "1px solid #ddd"
      }}
    >

      <h2 style={{ marginBottom: 10 }}>📁 PDFs</h2>

      {/* Upload button */}
      <button
        onClick={onUploadClick}
        style={{
          marginBottom: 10,
          padding: "8px 12px",
          background: "#007bff",
          color: "white",
          border: "none",
          borderRadius: 6,
          cursor: "pointer"
        }}
      >
        + Upload PDF
      </button>

      {/* Search box */}
      <input
        placeholder="Search PDFs..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{
          width: "100%",
          padding: 8,
          marginBottom: 10,
          borderRadius: 6,
          border: "1px solid #ccc"
        }}
      />

      {/* File list */}
      <div style={{ marginTop: 10 }}>
        {filteredFiles.length === 0 ? (
          <p style={{ color: "#888" }}>No PDFs found</p>
        ) : (
          filteredFiles.map((f) => (
            <div
              key={f}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "8px",
                marginBottom: 6,
                background: selectedFiles.includes(f) ? "#e8f0ff" : "#fff",
                border: "1px solid #eee",
                borderRadius: 6,
                cursor: "pointer"
              }}
            >

              {/* select */}
              <label
                style={{
                  display: "flex",
                  gap: 8,
                  alignItems: "center",
                  cursor: "pointer"
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedFiles.includes(f)}
                  onChange={() => toggle(f)}
                />
                📄 {f}
              </label>

              {/* delete */}
              <button
                onClick={() => onDelete(f)}
                style={{
                  color: "red",
                  border: "none",
                  background: "transparent",
                  cursor: "pointer",
                  fontSize: 16
                }}
              >
                🗑
              </button>

            </div>
          ))
        )}
      </div>
    </div>
  );
}