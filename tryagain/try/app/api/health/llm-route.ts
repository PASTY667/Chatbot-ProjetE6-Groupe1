// app/api/health/route.ts
import { NextResponse } from "next/server";
import { checkHealth } from "@/lib/health";

export async function GET() {
  try {
    const baseUrl = process.env.BACKEND_URL!;
    const status = await checkHealth(baseUrl);

    const healthy = status.status_ok && status.chroma_ok && status.ollama_ok && status.jwt_secret_ok;

    return NextResponse.json(status, {
      status: healthy ? 200 : 503,
      headers: {
        "Cache-Control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        status_ok: false,
        chroma_ok:false,
        ollama_ok: false,
        jwt_secret_ok: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      {
        status: 503,
      }
    );
  }
}