export type HealthStatus = {
  status_ok: boolean;
  chroma_ok:boolean;
  ollama_ok: boolean;
  jwt_secret_ok: boolean;
};

export async function checkHealth(baseUrl: string): Promise<HealthStatus> {
  const res = await fetch(`${baseUrl}/health`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ??`Health check failed (${res.status})`);
  }

  return res.json();
}