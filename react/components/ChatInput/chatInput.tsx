"use client";

import React, { useState } from "react";
import style from "@/components/ChatInput/chatInput.module.css";

type Props = {
  onSend: (message: string) => void | Promise<void>;
  disabled?: boolean;
};

export default function ChatInput({ onSend, disabled = false }: Props) {
  const [message, setMessage] = useState("");

  const handleSend = async () => {
    if (!message.trim() || disabled) return;
    await onSend(message);
    setMessage("");
  };

  return (
    <div className={style.chatInput}>
      <textarea
        className={style.textInput}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Poser une question..."
        disabled={disabled}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            void handleSend();
          }
        }}
      />

      <input
        className={style.submitButton}
        type="submit"
        value={disabled ? "..." : ">"}
        onClick={() => void handleSend()}
        disabled={disabled}
      />
    </div>
  );
}
