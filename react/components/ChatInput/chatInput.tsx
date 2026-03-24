"use client";
import React, { useState } from "react";
import style from "@/components/ChatInput/chatInput.module.css";

type Props = {
  onSend: (message: string) => void;
};

export default function ChatInput({ onSend }: Props) {
  const [message, setMessage] = useState("");

  //fonction d'envoi
  const handleSend = async () => {
    //Empêche d’envoyer une chaîne vide ou juste des espaces
    if (!message.trim()) return;

    onSend(message);
    // Vide l'input après l'envoi
    setMessage("");
  };

  return (
    <div className={style.chatInput}>
      <input
        className={style.textInput}
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Poser une question..."
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSend();
        }}
      />
      
      {/* BOUTON SOUMETTRE LE MESSAGE */}
      <input className={style.submitButton} type="submit" value=">" onClick={handleSend} />
    </div>
  );
}
