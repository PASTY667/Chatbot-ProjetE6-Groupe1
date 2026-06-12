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
  files?: File[];
  streaming?: boolean;
};

export type ChatSession = {
  id: string;
  title: string;
  messages: ChatMessage[];
};

function createSession(index: number): ChatSession {
  return {
    id: `c-${Date.now()}-${index}`,
    title: `Conversation ${index}`,
    messages: [],
  };
}

export default function Home() {
  const { status, data } = useSession();
  const router = useRouter();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [storageError, setStorageError] = useState("");

  const persistSession = async (session: ChatSession) => {
    const response = await fetch("/api/chat-sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: session.id, title: session.title }),
    });
    const data = (await response.json().catch(() => ({}))) as { detail?: string };

    if (!response.ok) {
      setStorageError(data.detail ?? "Sauvegarde des conversations indisponible.");
      return;
    }

    setStorageError("");
  };

  const persistMessages = async (sessionId: string, messages: ChatMessage[]) => {
    const response = await fetch(`/api/chat-sessions/${encodeURIComponent(sessionId)}/messages`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: messages.map(({ id, role, content }) => ({ id, role, content })),
      }),
    });
    const data = (await response.json().catch(() => ({}))) as { detail?: string };

    if (!response.ok) {
      setStorageError(data.detail ?? "Sauvegarde des messages indisponible.");
      return;
    }

    setStorageError("");
  };

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [router, status]);

  useEffect(() => {
    if (status !== "authenticated") {
      return;
    }

    let cancelled = false;

    async function loadSessions() {
      const response = await fetch("/api/chat-sessions", { cache: "no-store" });
      const data = (await response.json().catch(() => ({}))) as {
        sessions?: ChatSession[];
      };
      const loadedSessions = data.sessions ?? [];

      if (cancelled) {
        return;
      }

      if (response.ok && loadedSessions.length > 0) {
        setSessions(loadedSessions);
        setActiveSessionId(loadedSessions[0].id);
        setStorageError("");
        return;
      }

      if (!response.ok) {
        setStorageError(
          (data as { detail?: string }).detail ?? "Sauvegarde des conversations indisponible.",
        );
      }

      const firstSession = createSession(1);
      setSessions([firstSession]);
      setActiveSessionId(firstSession.id);
      if (response.ok) {
        void persistSession(firstSession);
      }
    }

    void loadSessions();

    return () => {
      cancelled = true;
    };
  }, [status]);

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
    void persistSession(nextSession);
  };

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
  };

  const handleRenameSession = (sessionId: string, title: string) => {
    const trimmedTitle = title.trim();
    if (!trimmedTitle) return;

    setSessions((prev) =>
      prev.map((session) =>
        session.id === sessionId ? { ...session, title: trimmedTitle } : session,
      ),
    );

    void fetch(`/api/chat-sessions/${encodeURIComponent(sessionId)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: trimmedTitle }),
    })
      .then(async (response) => {
        const data = (await response.json().catch(() => ({}))) as { detail?: string };
        if (!response.ok) {
          setStorageError(data.detail ?? "Renommage indisponible.");
          return;
        }
        setStorageError("");
      })
      .catch(() => setStorageError("Renommage indisponible."));
  };

  const handleMessagesChange = (sessionId: string, messages: ChatMessage[], persist = false) => {
    setSessions((prev) =>
      prev.map((session) => (session.id === sessionId ? { ...session, messages } : session)),
    );

    if (persist) {
      void persistMessages(sessionId, messages);
    }
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
        onRenameSession={handleRenameSession}
        authStatus={status}
        displayName={data?.user?.name ?? null}
        canCreateSession={status === "authenticated"}
        storageError={storageError}
      />
      <User
        activeSession={activeSession}
        onMessagesChange={handleMessagesChange}
        isAuthenticated={status === "authenticated"}
      />
    </div>
  );
}
