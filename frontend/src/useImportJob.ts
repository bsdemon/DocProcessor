import useSWR from "swr";
import { fetchJob, type ImportJob } from "./api";

export function useImportJob(jobId: string | null) {
  const key = jobId ? ["import-job", jobId] : null;

  const { data, error, isLoading, mutate } = useSWR<ImportJob>(
    key,
    () => fetchJob(jobId!),
    {
      refreshInterval: (latest) => {
        if (!latest) return 1000;
        if (latest.status === "completed" || latest.status === "failed") return 0;
        return 1000;
      },
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    }
  );

  return {
    job: data ?? null,
    error,
    isLoading,
    refresh: mutate,
  };
}