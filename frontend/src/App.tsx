import { useMemo, useState } from "react";
import { uploadCsv } from "./api";
import { useImportJob } from "./useImportJob";
import "./App.css";

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { job, isLoading, error: jobError } = useImportJob(jobId);

  const isTotalKnown = !!job && job.total_rows > 0;

  const progress = useMemo(() => {
    if (!job) return 0;
    const { processed_rows, total_rows } = job;
    if (!total_rows) return 0;
    return Math.round((processed_rows / total_rows) * 100);
  }, [job]);

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

              {selectedFile && <span className="file-name">{selectedFile.name}</span>}
            </div>

            <button onClick={onUpload} disabled={!selectedFile || uploading}>
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>

          {error && <div className="error-box">{error}</div>}

          {/* job polling status */}
          {jobId && isLoading && !job && <div className="status-section">Loading job…</div>}

          {jobError && (
            <div className="error-box">
              Couldn’t fetch job status: {jobError instanceof Error ? jobError.message : "Unknown error"}
            </div>
          )}

          {job && (
            <div className="status-section">
              <div className={`badge ${job.status}`}>{job.status}</div>

              <div className={`progress-bar ${isTotalKnown ? "" : "indeterminate"}`}>
                {isTotalKnown ? (
                  <div className="progress-fill" style={{ width: `${progress}%` }} />
                ) : (
                  <div className="progress-indeterminate" />
                )}
              </div>

              <div className="progress-text">
                {job.processed_rows}
                {isTotalKnown ? ` / ${job.total_rows} rows (${progress}%)` : " rows processed"}
              </div>

              {job.status === "completed" && (
                <div className="summary">
                  <div>Total: {job.total_rows}</div>
                  <div>Success: {job.success_rows}</div>
                  <div>Failed: {job.failed_rows}</div>
                </div>
              )}

              {job.status === "failed" && <div className="error-box">{job.error || "Job failed"}</div>}
            </div>
          )}
        </div>
      </main>

      <footer className="footer">Built with Django + Celery + React</footer>
    </div>
  );
}