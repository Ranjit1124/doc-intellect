import { useMemo, useState } from "react";
import {
  IconEye,
  IconPdf,
  IconRefresh,
  IconSearch,
  IconTrash,
  IconUpload,
} from "./Icons";

const PAGE_SIZE = 8;
// const BASE = "https://ranjittommy08-pdfchatbot.hf.space";
// const BASE = "http://127.0.0.1:8000";
const BASE = "";

export default function FileTable({
  files,
  selected,
  setSelected,
  onDelete,
  onUploadClick,
  onRefresh,
  uploading,
  searchQuery,
  onSearchChange,
}) {
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return files;
    return files.filter((f) => f.toLowerCase().includes(q));
  }, [files, searchQuery]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * PAGE_SIZE;
  const pageFiles = filtered.slice(start, start + PAGE_SIZE);

  const toggleSelect = (file) => {
    if (selected.includes(file)) {
      setSelected(selected.filter((f) => f !== file));
    } else {
      setSelected([...selected, file]);
    }
  };

  const toggleAll = () => {
    const allSelected = pageFiles.every((f) => selected.includes(f));
    if (allSelected) {
      setSelected(selected.filter((f) => !pageFiles.includes(f)));
    } else {
      const merged = new Set([...selected, ...pageFiles]);
      setSelected([...merged]);
    }
  };

  const allPageSelected =
    pageFiles.length > 0 && pageFiles.every((f) => selected.includes(f));

  return (
    <div className="card">
      <div className="card-header">
        <h2>Document Library</h2>
        <div className="card-toolbar">
          <div className="toolbar-search">
            <IconSearch />
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => {
                onSearchChange(e.target.value);
                setPage(1);
              }}
            />
          </div>
          <button type="button" className="btn btn-ghost" onClick={onRefresh}>
            <IconRefresh />
            Refresh
          </button>
          <button
            type="button"
            className="btn btn-accent"
            onClick={onUploadClick}
            disabled={uploading}
          >
            <IconUpload />
            {uploading ? "Uploading..." : "Upload PDF"}
          </button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <IconPdf />
          </div>
          <h3>No documents yet</h3>
          <p>Upload a PDF to start chatting with your documents.</p>
          <button type="button" className="btn btn-primary" onClick={onUploadClick}>
            <IconUpload />
            Upload your first PDF
          </button>
        </div>
      ) : (
        <>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: 48 }}>
                    <input
                      type="checkbox"
                      checked={allPageSelected}
                      onChange={toggleAll}
                      aria-label="Select all on page"
                    />
                  </th>
                  <th>#</th>
                  <th>File Name</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {pageFiles.map((f, i) => (
                  <tr
                    key={f}
                    className={selected.includes(f) ? "selected-row" : ""}
                  >
                    <td>
                      <input
                        type="checkbox"
                        checked={selected.includes(f)}
                        onChange={() => toggleSelect(f)}
                        aria-label={`Select ${f}`}
                      />
                    </td>
                    <td style={{ color: "var(--text-secondary)" }}>
                      {String(start + i + 1).padStart(2, "0")}
                    </td>
                    <td>
                      <div className="file-cell">
                        <div className="file-icon">
                          <IconPdf />
                        </div>
                        <span className="file-name" title={f}>
                          {f}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-success">Indexed</span>
                    </td>
                    <td>
                      <div className="action-group">
                        <button
                          type="button"
                          className="btn-icon"
                          title="View PDF"
                          onClick={() => window.open(`${BASE}/uploads/${f}`, "_blank")}
                        >
                          <IconEye />
                        </button>
                        <button
                          type="button"
                          className="btn-icon danger"
                          title="Delete"
                          onClick={() => onDelete(f)}
                        >
                          <IconTrash />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="table-footer">
            <div className="table-footer-info">
              Showing {start + 1}–{Math.min(start + PAGE_SIZE, filtered.length)} of{" "}
              {filtered.length} documents
              {selected.length > 0 && ` · ${selected.length} selected`}
            </div>
            <div className="pagination">
              <button
                type="button"
                className="page-btn"
                disabled={currentPage === 1}
                onClick={() => setPage((p) => p - 1)}
              >
                ‹
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(
                  (p) =>
                    p === 1 ||
                    p === totalPages ||
                    Math.abs(p - currentPage) <= 1
                )
                .reduce((acc, p, idx, arr) => {
                  if (idx > 0 && p - arr[idx - 1] > 1) acc.push("...");
                  acc.push(p);
                  return acc;
                }, [])
                .map((p, i) =>
                  p === "..." ? (
                    <span key={`ellipsis-${i}`} style={{ padding: "0 4px", color: "var(--text-muted)" }}>
                      …
                    </span>
                  ) : (
                    <button
                      key={p}
                      type="button"
                      className={`page-btn ${currentPage === p ? "active" : ""}`}
                      onClick={() => setPage(p)}
                    >
                      {String(p).padStart(2, "0")}
                    </button>
                  )
                )}
              <button
                type="button"
                className="page-btn"
                disabled={currentPage === totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                ›
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
