import { NextRequest, NextResponse } from "next/server";
import { renameChatSession } from "@/lib/chat-db";
import { getSessionUsername } from "@/lib/session-user";

type RouteContext = {
  params: Promise<{
    sessionId: string;
  }>;
};

export async function PATCH(request: NextRequest, context: RouteContext) {
  try {
    const username = await getSessionUsername(request);

    if (!username) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }

    const { sessionId } = await context.params;
    const body = (await request.json().catch(() => ({}))) as {
      title?: string;
    };
    const title = body.title?.trim();

    if (!title) {
      return NextResponse.json({ detail: "Missing title" }, { status: 400 });
    }

    await renameChatSession(username, sessionId, title);
    return NextResponse.json({ session: { id: sessionId, title } });
  } catch (error) {
    console.error("Unable to rename chat session:", error);
    return NextResponse.json(
      { detail: "Impossible de renommer la conversation. Verifiez les droits de la base de donnees." },
      { status: 503 },
    );
  }
}
