import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";

export async function POST(request: NextRequest) {
  const session = await getToken({ req: request, secret: process.env.NEXTAUTH_SECRET });

  const username = typeof session?.username === "string" ? session.username : session?.name;

  if (!username) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const backendUrl = process.env.BACKEND_API_URL ?? "http://localhost:8000";
  const adminKey = process.env.BACKEND_ADMIN_KEY;

  if (!adminKey) {
    return NextResponse.json({ detail: "BACKEND_ADMIN_KEY is not configured" }, { status: 500 });
  }

  const response = await fetch(`${backendUrl}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: adminKey, subject: username }),
  });

  const data = await response.json().catch(() => ({}));
  return NextResponse.json(
    {
      ...data,
      username,
      role: session?.role ?? "user",
      groups: session?.groups ?? [],
    },
    { status: response.status },
  );
}
