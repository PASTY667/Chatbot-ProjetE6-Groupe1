import { NextRequest, NextResponse } from "next/server";
import { createChatSession, listChatSessions } from "@/lib/chat-db";
import { getSessionUsername } from "@/lib/session-user";

export async function GET(request: NextRequest) {
  try {
    const username = await getSessionUsername(request);

    if (!username) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }

    const sessions = await listChatSessions(username);
    return NextResponse.json({ sessions });
  } catch (error) {
    console.error("Unable to load chat sessions:", error);
    return NextResponse.json(
      { detail: "Sauvegarde des conversations indisponible. Verifiez les droits de la base de donnees." },
      { status: 503 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const username = await getSessionUsername(request);

    if (!username) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }

    const body = (await request.json().catch(() => ({}))) as {
      id?: string;
      title?: string;
    };
    const id = body.id?.trim();
    const title = body.title?.trim() || "Nouvelle conversation";

    if (!id) {
      return NextResponse.json({ detail: "Missing chat session id" }, { status: 400 });
    }

    await createChatSession(username, id, title);
    return NextResponse.json({ session: { id, title, messages: [] } });
  } catch (error) {
    console.error("Unable to create chat session:", error);
    return NextResponse.json(
      { detail: "Impossible de sauvegarder la conversation. Verifiez les droits de la base de donnees." },
      { status: 503 },
    );
  }
}
