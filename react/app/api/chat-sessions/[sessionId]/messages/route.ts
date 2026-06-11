import { NextRequest, NextResponse } from "next/server";
import { replaceChatMessages, type StoredChatMessage } from "@/lib/chat-db";
import { getSessionUsername } from "@/lib/session-user";

type RouteContext = {
  params: Promise<{
    sessionId: string;
  }>;
};

export async function PUT(request: NextRequest, context: RouteContext) {
  try {
    const username = await getSessionUsername(request);

    if (!username) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }

    const { sessionId } = await context.params;
    const body = (await request.json().catch(() => ({}))) as {
      messages?: StoredChatMessage[];
    };
    const messages =
      body.messages?.filter(
        (message) =>
          typeof message.id === "string" &&
          (message.role === "user" || message.role === "assistant") &&
          typeof message.content === "string",
      ) ?? [];

    await replaceChatMessages(username, sessionId, messages);
    return NextResponse.json({ ok: true });
  } catch (error) {
    console.error("Unable to save chat messages:", error);
    return NextResponse.json(
      { detail: "Impossible de sauvegarder les messages. Verifiez les droits de la base de donnees." },
      { status: 503 },
    );
  }
}
