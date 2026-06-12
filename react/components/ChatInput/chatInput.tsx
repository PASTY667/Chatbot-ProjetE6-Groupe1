"use client";

import React, { useState } from "react";
import style from "@/components/ChatInput/chatInput.module.css";

type Props = {
  onSend: (message: string) => void | Promise<void>;
  disabled?: boolean;
};

export default function ChatInput({ onSend, disabled = false }: Props) {
  const [message, setMessage] = useState("");

  //Fonction d'envoi
  const handleSend = async () => {
    //Empêche d’envoyer une chaîne vide ou juste des espaces
    if (!message.trim() || disabled) return;
    
    await onSend(message);
    // Vide l'input après l'envoi
    setMessage("");
  };

  return (
    <div className={style.chatInput}>
      {/* Configuration du champ d'input */}
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

{/* BOUTON SOUMETTRE LE MESSAGE */}
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
