"use client";
import React, { useState } from "react";
import style from "@/components/ChatInput/chatInput.module.css";

type Props = {
  onSend: (message: string) => void;
};

export default function ChatInput({ onSend }: Props) {
  const [message, setMessage] = useState("");

  //Fonction d'envoi
  const handleSend = async () => {
    //Empêche d’envoyer une chaîne vide ou juste des espaces
    if (!message.trim()) return;

    onSend(message);
    // Vide l'input après l'envoi
    setMessage("");
  };

  //Pour mettre, automatiquement, la première lettre du message en majuscule
  const capitalizeFirstLetter = (value: string) => {
  if (!value) return value;
  return value.charAt(0).toUpperCase() + value.slice(1);
};


  return (
    <div className={style.chatInput}>
      {/* Configuration du champ d'input */}
      <textarea
        className={style.textInput}
        value={message}
        onChange={(e) => {setMessage(capitalizeFirstLetter(e.target.value))}}
        placeholder="Poser une question..."
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            handleSend();
          }
        }}
      />

      {/* BOUTON SOUMETTRE LE MESSAGE */}
      <input
        className={style.submitButton}
        type="submit"
        value=">"
        onClick={handleSend}
      />
    </div>
  );
}
