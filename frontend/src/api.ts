const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type ImportStatus = "pending" | "processing" | "completed" | "failed";

export type ImportSummary = {
  total: number;
  success: number;
  failed: number;
};
export type ImportJob = {
  id: string;
  status: ImportStatus;
  progress: number;

  total_rows: number;
  processed_rows: number;
  success_rows: number;
  failed_rows: number;

  error: string;
  file: string;
  created_at: string;
  updated_at: string;
};

export async function uploadCsv(file: File): Promise<{ id: string }> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/imports/`, {
    method: "POST",
    headers: { "X-API-KEY": import.meta.env.VITE_IMPORT_API_KEY },
    body: form,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Upload failed (${res.status})`);
  }

  return res.json();
}

export async function fetchJob(jobId: string): Promise<ImportJob> {
  const res = await fetch(
    `${API_BASE_URL}/api/imports/${jobId}/`, {
      headers: { "X-API-KEY": import.meta.env.VITE_IMPORT_API_KEY },
    }
  );

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `Fetch failed (${res.status})`);
  }

  return res.json();
}
