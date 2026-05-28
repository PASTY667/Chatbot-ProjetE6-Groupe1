export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
};

export async function fetchToken(baseUrl: string, apiKey: string, subject = "frontend-user"): Promise<TokenResponse> {
  const res = await fetch(`${baseUrl}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, subject }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Auth failed (${res.status})`);
  }

  return res.json();
}