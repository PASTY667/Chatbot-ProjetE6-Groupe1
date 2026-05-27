import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  try {
    // Check health endpoints
    const chromaUrl = process.env.CHROMA_URL || "http://localhost:8000";
    const ollamaUrl = process.env.OLLAMA_URL || "http://localhost:11434";
    const jwtSecret = process.env.NEXTAUTH_SECRET;

    const chromaHealth = await fetch(`${chromaUrl}/api/v1/heartbeat`)
      .then(() => true)
      .catch(() => false);

    const ollamaHealth = await fetch(`${ollamaUrl}/api/tags`)
      .then(() => true)
      .catch(() => false);

    const jwtSecretOk = !!jwtSecret;

    const allOk = chromaHealth && ollamaHealth && jwtSecretOk;

    return NextResponse.json(
      {
        status_ok: allOk,
        chroma_ok: chromaHealth,
        ollama_ok: ollamaHealth,
        jwt_secret_ok: jwtSecretOk,
      },
      { status: allOk ? 200 : 503 }
    );
  } catch (error) {
    console.error("Health check error:", error);
    return NextResponse.json(
      {
        status_ok: false,
        chroma_ok: false,
        ollama_ok: false,
        jwt_secret_ok: false,
      },
      { status: 503 }
    );
  }
}