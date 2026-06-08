import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const authorization = request.headers.get("authorization");

  if (!authorization) {
    return NextResponse.json({ detail: "Missing bearer token" }, { status: 401 });
  }

  const body = await request.text();
  const backendUrl = process.env.BACKEND_API_URL ?? "http://localhost:8000";

  const response = await fetch(`${backendUrl}/chat/query/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      authorization,
    },
    body,
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "text/plain; charset=utf-8",
    },
  });
}
