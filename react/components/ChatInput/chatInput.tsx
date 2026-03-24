import React, { useState } from "react";


type Message = {
  role: "user" | "assistant";
  content: string;
};

const ChatInputConst = () => {
  const [message, setMessage] = useState("");

  //fonction d'envoi
  const handleSend = async () => {
    //Empêche d’envoyer une chaîne vide ou juste des espaces
    // if (!messages.trim()) return;

    setMessage("");
  }
};

export default function ChatInput(){

}