"use client";

import { useEffect, useMemo, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

import Sidebar from "@/components/sidebar/sidebar";
import User from "@/app/user/page";

import style from "./page.module.css";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
};

export type ChatSession = {
  id: string;
  title: string;
  messages: ChatMessage[];
};

function createSession(index: number): ChatSession {
  return {
    id: `session-${Date.now()}-${index}`,
    title: `Conversation ${index}`,
    messages: [],
  };
}

export default function Home() {
  const { status, data } = useSession();
  const router = useRouter();
  const [sessions, setSessions] = useState<ChatSession[]>(() => [createSession(1)]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(
    () => sessions[0]?.id ?? null,
  );

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [router, status]);

  const activeSession = useMemo(
    () => sessions.find((session) => session.id === activeSessionId) ?? sessions[0] ?? null,
    [sessions, activeSessionId],
  );

  const handleCreateSession = () => {
    if (status !== "authenticated") {
      return;
    }

    const nextSession = createSession(sessions.length + 1);
    setSessions((prev) => [nextSession, ...prev]);
    setActiveSessionId(nextSession.id);
  };

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
  };

  const handleMessagesChange = (sessionId: string, messages: ChatMessage[]) => {
    setSessions((prev) =>
      prev.map((session) => (session.id === sessionId ? { ...session, messages } : session)),
    );
  };

  if (status === "loading" || status === "unauthenticated") {
    return null;
  }

  return (
    <div className={style.shell}>
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSession?.id ?? null}
        onCreateSession={handleCreateSession}
        onSelectSession={handleSelectSession}
        authStatus={status}
        displayName={data?.user?.name ?? null}
        canCreateSession={status === "authenticated"}
      />
      <User
        activeSession={activeSession}
        onMessagesChange={handleMessagesChange}
        isAuthenticated={status === "authenticated"}
      />
    </div>
  );
}
