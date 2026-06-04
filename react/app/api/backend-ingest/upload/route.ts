import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const authorization = request.headers.get("authorization");

  if (!authorization) {
    return NextResponse.json({ detail: "Missing bearer token" }, { status: 401 });
  }

  const incomingForm = await request.formData();
  const file = incomingForm.get("file");

  if (!(file instanceof File)) {
    return NextResponse.json({ detail: "Missing file" }, { status: 400 });
  }

  const backendForm = new FormData();
  backendForm.set("file", file);
  backendForm.set("scope", String(incomingForm.get("scope") ?? "user"));

  const chatId = incomingForm.get("chat_id");
  if (chatId) {
    backendForm.set("chat_id", String(chatId));
  }

  const collectionName = incomingForm.get("collection_name");
  if (collectionName) {
    backendForm.set("collection_name", String(collectionName));
  }

  const docId = incomingForm.get("doc_id");
  if (docId) {
    backendForm.set("doc_id", String(docId));
  }

  const backendUrl = process.env.BACKEND_API_URL ?? "http://localhost:8000";
  const response = await fetch(`${backendUrl}/ingest/upload`, {
    method: "POST",
    headers: { authorization },
    body: backendForm,
  });

  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}
