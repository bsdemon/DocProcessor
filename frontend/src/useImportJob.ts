import { useEffect, useRef, useState } from "react";
import { fetchJob, type ImportJob } from "./api";


type State =
  | { kind: "idle" }
  | { kind: "loading"; jobId: string }
  | { kind: "ready"; job: ImportJob }
  | { kind: "error"; message: string; jobId?: string };

export function useImportJob(jobId: string | null, intervalMs = 1000) {
  const [state, setState] = useState<State>({ kind: "idle" });
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    if (!jobId) {
      setState({ kind: "idle" });
      return;
    }

    let cancelled = false;

    async function tick() {
      try {
        if (cancelled) return;
        setState((prev) => (prev.kind === "ready" ? prev : { kind: "loading", jobId }));

        const job = await fetchJob(jobId);
        if (cancelled) return;

        setState({ kind: "ready", job });

        // stop polling when terminal state
        if (job.status === "completed" || job.status === "failed") {
          if (timerRef.current) window.clearInterval(timerRef.current);
          timerRef.current = null;
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Unknown error";
        if (!cancelled) setState({ kind: "error", message: msg, jobId });
      }
    }

    tick();

    timerRef.current = window.setInterval(tick, intervalMs);

    return () => {
      cancelled = true;
      if (timerRef.current) window.clearInterval(timerRef.current);
      timerRef.current = null;
    };
  }, [jobId, intervalMs]);

  return state;
}

