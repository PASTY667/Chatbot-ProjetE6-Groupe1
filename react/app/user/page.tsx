"use client";

import Image from "next/image";
import { useRef, useState } from "react";

import style from "@/app/user/user.module.css";
import uploadIcon from "@/assets/upload-file.png";
import ChatInput from "@/components/ChatInput/chatInput";
import type { ChatMessage, ChatSession } from "@/app/page";

type UploadedFile = {
  id: string;
  file: File;
  status: "pending" | "uploading" | "done" | "error";
  detail?: string;
};

type IngestResponse = {
  collection_name: string;
  doc_id: string;
  chunks_count: number;
  inserted_id_count: number;
  source_path: string;
};

type UserProps = {
  activeSession: ChatSession | null;
  onMessagesChange: (sessionId: string, messages: ChatMessage[], persist?: boolean) => void;
  isAuthenticated: boolean;
};

export default function User({ activeSession, onMessagesChange, isAuthenticated }: UserProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploadError, setUploadError] = useState("");
  const [isSending, setIsSending] = useState(false);
  const assistantMessageIdRef = useRef<string | null>(null);

  const messages = activeSession?.messages ?? [];

  const updateMessages = (nextMessages: ChatMessage[], persist = false) => {
    if (!activeSession) return;
    onMessagesChange(activeSession.id, nextMessages, persist);
  };

  const uploadFile = async (file: File, id: string) => {
    const token = localStorage.getItem("backend_access_token");
    const chatId = activeSession?.id ?? "user";

    if (!token) {
      setFiles((prev) =>
        prev.map((item) =>
          item.id === id
            ? { ...item, status: "error", detail: "Connexion LDAP requise avant l'envoi." }
            : item,
        ),
      );
      setUploadError("Connectez-vous au LDAP pour envoyer un document.");
      return;
    }

    setFiles((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, status: "uploading", detail: undefined } : item,
      ),
    );

    const formData = new FormData();
    formData.set("file", file);
    formData.set("scope", "user");
    formData.set("chat_id", chatId);

    try {
      const response = await fetch("/api/backend-ingest/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = (await response.json().catch(() => ({}))) as Partial<IngestResponse> & {
        detail?: string;
      };

      if (!response.ok) {
        throw new Error(data.detail ?? `Erreur ingestion (${response.status})`);
      }

      setFiles((prev) =>
        prev.map((item) =>
          item.id === id
            ? {
                ...item,
                status: "done",
                detail: `${data.chunks_count ?? 0} chunks dans ${data.collection_name ?? "collection"}`,
              }
            : item,
        ),
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erreur ingestion";
      setFiles((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, status: "error", detail: message } : item,
        ),
      );
      setUploadError(message);
    }
  };

  const handleSendMessage = async (msg: string) => {
    const trimmed = msg.trim();
    if (!trimmed || isSending || !activeSession) return;

    const userMessage: ChatMessage = {
      id: `${Date.now()}-user`,
      role: "user",
      content: trimmed,
    };

    const assistantId = `${Date.now()}-assistant`;
    assistantMessageIdRef.current = assistantId;

    const nextMessages: ChatMessage[] = [
      ...messages,
      userMessage,
      { id: assistantId, role: "assistant", content: "", streaming: true },
    ];

    updateMessages(nextMessages);
    setIsSending(true);

    try {
      const token = localStorage.getItem("backend_access_token");
      if (!token) {
        throw new Error("Connexion LDAP requise pour interroger le chatbot.");
      }

      const chatId = activeSession.id;
      const hasSessionFile = files.some((file) => file.status === "done");

      const response = await fetch("/api/backend-chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: trimmed,
          original_query: trimmed,
          history: messages.map(({ role, content }) => ({ role, content })),
          answer_mode: "hybrid",
          allow_general_knowledge: true,
          k: 2,
          use_official: true,
          include_user_collection: hasSessionFile,
          chat_id: chatId,
        }),
      });

      if (!response.ok || !response.body) {
        const err = await response.text().catch(() => "");
        throw new Error(err || `Erreur chat (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        if (!value) continue;
        const chunk = decoder.decode(value, { stream: true });
        if (!chunk) continue;

        assistantContent += chunk;
        updateMessages(
          nextMessages.map((item) =>
            item.id === assistantId ? { ...item, content: assistantContent, streaming: true } : item,
          ),
        );
      }

      const tail = decoder.decode();
      if (tail) {
        assistantContent += tail;
      }

      const finalMessages = nextMessages.map((item) =>
          item.id === assistantId ? { ...item, content: assistantContent, streaming: false } : item,
        );
      updateMessages(finalMessages, true);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erreur chat";
      const errorMessages = nextMessages.map((item) =>
          item.id === assistantId ? { ...item, content: message, streaming: false } : item,
        );
      updateMessages(errorMessages, true);
    } finally {
      assistantMessageIdRef.current = null;
      setIsSending(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const selectedFiles = Array.from(e.target.files);
    const nextFiles: UploadedFile[] = selectedFiles.map((file, index) => ({
      id: `${Date.now()}-${index}-${file.name}`,
      file,
      status: "pending",
    }));

    setUploadError("");
    setFiles((prev) => [...prev, ...nextFiles]);
    nextFiles.forEach((item) => {
      void uploadFile(item.file, item.id);
    });
    e.target.value = "";
  };

  const removeFile = (indexToRemove: number) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  return (
    <main className={style.main}>
      <div className={style.newchatPage}>
        <div className={style.newchatHeader}>
          <p className={style.kicker}>Chatbot souverain pour intranet</p>
          <h1 className={style.newchatTitle}>{activeSession?.title ?? "Conversation"}</h1>
          <p className={style.statusLine}>
            {isAuthenticated ? "Connexion LDAP active." : "Connectez vous pour echanger avec le chatbot."}
          </p>
        </div>

        <div className={style.grid}>
          {messages.length === 0 && (
            <div className={style.emptyState}>
              Creez une conversation ou connectez-vous pour interroger le chatbot.
            </div>
          )}

          {messages.map((msg) => (
            <div
              className={`${style.message} ${msg.role === "user" ? style.userMessage : style.assistantMessage}`}
              key={msg.id}
            >
              {msg.content}
              {msg.streaming && <span className={style.streamingCursor}>|</span>}
            </div>
          ))}
        </div>

        <div className={style.newchatInput}>
          <div className={style.uploadSection}>
            <label className={style.uploadButton} htmlFor="upload-file">
              <Image className={style.uploadIcon} src={uploadIcon} alt="i" /> PDF
            </label>

            <input
              id="upload-file"
              type="file"
              className={style.addButton}
              accept=".pdf,.txt,.md"
              multiple
              onChange={handleFileChange}
              disabled={!isAuthenticated}
            />

            <div className={style.fileList}>
              {files.map((file, index) => (
                <div key={file.id} className={style.fileItem}>
                  <button className={style.deleteButton} onClick={() => removeFile(index)} type="button">
                    X
                  </button>
                  <p>{file.file.name}</p>
                  <span className={`${style.fileStatus} ${style[file.status]}`}>
                    {file.status === "uploading" ? "ingestion..." : file.status}
                  </span>
                  {file.detail && <span className={style.fileDetail}>{file.detail}</span>}
                </div>
              ))}
            </div>
            {uploadError && <p className={style.uploadError}>{uploadError}</p>}
          </div>

          <ChatInput onSend={handleSendMessage} disabled={isSending || !isAuthenticated} />
        </div>
      </div>
    </main>
  );
}
