"use client";

import Image from "next/image";
import { useRef, useState } from "react";
import { Grid } from "@mui/material";

import style from "@/app/user/user.module.css";
import uploadIcon from "@/assets/upload-file.png";
import ChatInput from "@/components/ChatInput/chatInput";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
};

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

export default function User() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploadError, setUploadError] = useState("");
  const [isSending, setIsSending] = useState(false);
  const assistantMessageIdRef = useRef<string | null>(null);

  const uploadFile = async (file: File, id: string) => {
    const token = localStorage.getItem("backend_access_token");
    const chatId = localStorage.getItem("backend_subject") ?? "user";

    if (!token) {
      setFiles((prev) =>
        prev.map((item) =>
          item.id === id
            ? { ...item, status: "error", detail: "Connectez-vous avant l'envoi." }
            : item,
        ),
      );
      setUploadError("Connectez-vous avant d'envoyer un document.");
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

  //Gérer l'envoi d'un message
  const handleSendMessage = async (msg: string) => {
    const trimmed = msg.trim();
    if (!trimmed || isSending) return;

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: "user",
      content: trimmed,
    };
    const assistantId = `${Date.now()}-assistant`;
    assistantMessageIdRef.current = assistantId;

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: assistantId, role: "assistant", content: "", streaming: true },
    ]);
    setIsSending(true);

    try {
      const token = localStorage.getItem("backend_access_token");
      if (!token) {
        throw new Error("Connectez-vous avant de poser une question.");
      }

      const chatId = localStorage.getItem("backend_subject") ?? "user";
      const response = await fetch("/api/backend-chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: trimmed,
          k: 2,
          use_official: true,
          include_user_collection: true,
          chat_id: chatId,
        }),
      });

      if (!response.ok || !response.body) {
        const err = await response.text().catch(() => "");
        throw new Error(err || `Erreur chat (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        if (!value) continue;
        const chunk = decoder.decode(value, { stream: true });

        if (chunk) {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantId
                ? { ...item, content: item.content + chunk, streaming: true }
                : item,
            ),
          );
        }
      }

      const tail = decoder.decode();
      if (tail) {
        setMessages((prev) =>
          prev.map((item) =>
            item.id === assistantId
              ? { ...item, content: item.content + tail, streaming: true }
              : item,
          ),
        );
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erreur chat";
      setMessages((prev) =>
        prev.map((item) =>
          item.id === assistantMessageIdRef.current
            ? { ...item, content: message, streaming: false }
            : item,
        ),
      );
    } finally {
      assistantMessageIdRef.current = null;
      setIsSending(false);
      setMessages((prev) =>
        prev.map((item) =>
          item.role === "assistant" && item.streaming ? { ...item, streaming: false } : item,
        ),
      );
    }
  };

  //Gérer l'envoi des fichiers
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

  //Gérer la suppression des fichiers
  const removeFile = (indexToRemove: number) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  return (
    <main className={`${style.main} ${messages.length === 0 ? style.centered : ""}`}>
      <div className={style.newchatPage}>
        {messages.length === 0 && (
          <div className={style.newchatHeader}>
            <h1 className={style.newchatTitle}>Franklin</h1>
          </div>
        )}

        <Grid className={style.grid}>
          {messages.map((msg) => (
            <div className={style.message} key={msg.id}>
              {msg.content}
              {msg.streaming && <span className={style.streamingCursor}>|</span>}
            </div>
          ))}
        </Grid>

        <div
          className={`${style.newchatInput} ${
            messages.length === 0 ? style.inputCentered : style.inputBottom
          }`}
        >
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
            />

            <div className={style.fileList}>
              {files.map((file, index) => (
                <div key={file.id} className={style.fileItem}>
                  <button className={style.deleteButton} onClick={() => removeFile(index)}>
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

          <ChatInput onSend={handleSendMessage} disabled={isSending} />
        </div>
        <div className={style.footer}>footer</div>
      </div>
    </main>
  );
}
