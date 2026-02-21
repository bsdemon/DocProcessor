import { useMemo, useState } from "react";
import { uploadCsv } from "./api";
import { useImportJob } from "./useImportJob";
import "./App.css";

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const state = useImportJob(jobId, 1000);
  const isTotalKnown = state.kind === "ready" && state.job.total_rows > 0;

  const progress = useMemo(() => {
    if (state.kind !== "ready") return 0;
    const { processed_rows, total_rows } = state.job;
    if (!total_rows) return 0;
    return Math.round((processed_rows / total_rows) * 100);
  }, [state]);

  async function onUpload() {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);

    try {
      const res = await uploadCsv(selectedFile);
      setJobId(res.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>CSV Import Dashboard</h1>
      </header>

      <main className="container">
        <div className="card">
          <h2>Upload CSV</h2>

          <div className="upload-row">
            <div className="file-upload">
              <input
                id="fileInput"
                type="file"
                accept=".csv"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                hidden
              />

              <label htmlFor="fileInput" className="file-button">
                {selectedFile ? "Change File" : "Choose CSV File"}
              </label>

              {selectedFile && (
                <span className="file-name">
                  {selectedFile.name}
                </span>
              )}
            </div>
            <button onClick={onUpload} disabled={!selectedFile || uploading}>
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>

          {error && <div className="error-box">{error}</div>}

          {state.kind === "ready" && (
            <div className="status-section">
              <div className={`badge ${state.job.status}`}>
                {state.job.status}
              </div>

              <div className={`progress-bar ${isTotalKnown ? "" : "indeterminate"}`}>
                {isTotalKnown ? (
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                ) : (
                  <div className="progress-indeterminate" />
                )}
              </div>

              <div className="progress-text">
                {state.job.processed_rows}
                {isTotalKnown ? ` / ${state.job.total_rows} rows (${progress}%)` : " rows processed"}
              </div>

              {state.job.status === "completed" && (
                <div className="summary">
                  <div>Total: {state.job.total_rows}</div>
                  <div>Success: {state.job.success_rows}</div>
                  <div>Failed: {state.job.failed_rows}</div>
                </div>
              )}

              {state.job.status === "failed" && (
                <div className="error-box">
                  {state.job.error || "Job failed"}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        Built with Django + Celery + React
      </footer>
    </div>
  );
}
