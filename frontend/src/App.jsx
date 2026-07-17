import { useEffect, useRef, useState } from "react";
import { getFiles, uploadPDF, deleteFile } from "./api/api";
import { me } from "./api/api";

import FileTable from "./components/FileTable";
import ChatBox from "./components/ChatBox";
import NavSidebar from "./components/NavSidebar";
import Header from "./components/Header";
import "./App.css";
import Login from "./components/Login";

export default function App() {
  const [user, setUser] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeView, setActiveView] = useState("documents");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const fileInputRef = useRef(null);

  const loadFiles = async () => {
    if (!user) return;
    try {
      const data = await getFiles();
      setFiles(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error loading files:", err);
      setFiles([]);
    }
  };

  useEffect(() => {
    const check = async () => {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const data = await me();
          setUser(data);
        } catch (e) {
          console.warn("Auth check failed", e);
          localStorage.removeItem("access_token");
          setUser(null);
        }
      } else {
        setUser(null);
      }
    };
    check();
  }, []);

  useEffect(() => {
    if (user) {
      loadFiles();
    }
  }, [user]);

  const handleUpload = async (pickedFile) => {
    if (!pickedFile || uploading) return;

    setUploading(true);
    try {
      await uploadPDF(pickedFile);
      if (fileInputRef.current) fileInputRef.current.value = "";
      await loadFiles();
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = (e) => {
    const picked = e.target.files?.[0];
    if (picked) handleUpload(picked);
  };

  const remove = async (name) => {
    await deleteFile(name);
    setSelectedFiles((prev) => prev.filter((f) => f !== name));
    loadFiles();
  };

  if (!user) {
    return (
      <div className="dashboard">
        <Login onAuth={(u) => setUser(u)} />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <NavSidebar
        activeView={activeView}
        setActiveView={setActiveView}
        fileCount={files.length}
        selectedCount={selectedFiles.length}
      />

      <div className="main-wrapper">
        <Header
          title={activeView === "documents" ? "Documents" : "AI Chat"}
          subtitle={
            activeView === "documents"
              ? "Manage and select PDFs for chat"
              : "Ask questions about your selected documents"
          }
          user={user}
          onLogout={() => {
            localStorage.removeItem("access_token");
            setUser(null);
            setFiles([]);
            setSelectedFiles([]);
            setChatMessages([]);
            setChatQuestion("");
          }}
          search={searchQuery}
          onSearchChange={setSearchQuery}
        />

        <main className="page-content">
          {activeView === "documents" ? (
            <div className="content-grid">
              <FileTable
                files={files}
                selected={selectedFiles}
                setSelected={setSelectedFiles}
                onDelete={remove}
                onUploadClick={() => fileInputRef.current?.click()}
                onRefresh={loadFiles}
                uploading={uploading}
                searchQuery={searchQuery}
                onSearchChange={setSearchQuery}
              />
              <ChatBox
                selectedFiles={selectedFiles}
                messages={chatMessages}
                setMessages={setChatMessages}
                question={chatQuestion}
                setQuestion={setChatQuestion}
                loading={chatLoading}
                setLoading={setChatLoading}
              />
            </div>
          ) : (
            <div className="content-grid single">
              <ChatBox
                selectedFiles={selectedFiles}
                messages={chatMessages}
                setMessages={setChatMessages}
                question={chatQuestion}
                setQuestion={setChatQuestion}
                loading={chatLoading}
                setLoading={setChatLoading}
              />
            </div>
          )}
        </main>
      </div>

      <input
        ref={fileInputRef}
        className="hidden-input"
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileChange}
      />
    </div>
  );
}
