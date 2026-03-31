import Image from "next/image";
import React, { useState } from "react";
import {
  TextField,
  Button,
  Container,
  Grid,
  LinearProgress,
  CircularProgress,
} from "@mui/material";

import style from "@/app/index/index.module.css";
import uploadIcon from "@/assets/upload-file.png";
import ChatInput from "@/components/ChatInput/chatInput";
import logo from "@/assets/frankLogo.png";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Index() {
  const [messages, setMessages] = useState<Message[]>([]);

  //Gérer l'envoi d'un message
  const handleSendMessage = (msg: string) => {
    const newMessage: Message = {
      role: "user",
      content: msg,
    };

    setMessages((prev) => [...prev, newMessage]);
  };

  return (
    <main className={style.main}>
      <div className={style.newchatPage}>
        {/* HEADER DE LA PAGE */}
        <div className={style.newchatHeader}>
          {/* <Image className={style.logo} src={} alt="" /> */}
          <h1 className={style.newchatTitle}>Franklin</h1>
        </div>

        <Grid className={style.grid}>
          {messages.map((msg, index) => (
            <div className={style.message} key={index}>{msg.content}</div>
          ))}
        </Grid>

        {/* ZONE D'INPUT */}
        <div className={style.newchatInput}>
          {/* UPLOAD UN FICHIER (PDF OU WORD) */}
          <div className={style.uploadSection}>
            <label htmlFor="upload-file" className={style.uploadButton}>
              <Image className={style.uploadIcon} src={uploadIcon} alt="i" />{" "}
              PDF
            </label>
            {/* <span id="file-name" className={style.fileName}></span> */}
            {/* A AJOUTER COMPOSANT POUR L'AFFICHAGE DES FICHIERS + IMAGE EXTENSION */}
            <input
              id="upload-file"
              type="file"
              className={style.addButton}
              accept=".doc, .docx, .pdf"
            />
          </div>

          {/* INPUT D'UN MESSAGE AU CHABOT */}
          <ChatInput onSend={handleSendMessage} />
        </div>
      </div>
    </main>
  );
}
