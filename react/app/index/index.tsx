import Image from "next/image";
import { useState } from "react";
import { Grid } from "@mui/material";

import style from "@/app/index/index.module.css";
import uploadIcon from "@/assets/upload-file.png";
import ChatInput from "@/components/ChatInput/chatInput";
import logo from "@/assets/frankLogo.png";

type Message = {
  role: "user" | "assistant";
  content: string;
  files:File[];
};

export default function Index() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [files, setFiles] = useState<File[]>([]);

  //Gérer l'envoi d'un message
  const handleSendMessage = (msg: string) => {
    const newMessage: Message = {
      role: "user",
      content: msg,
      files: [...files],
    };

    setMessages((prev) => [...prev, newMessage]);
    setFiles([]);
  };

  //Gérer l'envoi des fichiers
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;

    const selectedFiles = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...selectedFiles]);
    e.target.value = "";
  };

  //Gérer la suppression des fichiers
  const removeFile = (indexToRemove: number) => {
    setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
  };

  return (
    <main
      className={style.main}
    >
      <div className={style.newchatPage}>

        {/* HEADER DE LA PAGE */}
        {messages.length === 0 && (
          <div className={style.newchatHeader}>
            {/* <Image className={style.logo} src={} alt="" /> */}

            <h1 className={style.newchatTitle}>Franklin</h1>
          </div>
        )}

        <Grid className={style.grid}>
          <div className={style.question}>
          {messages.map((msg, index) => (
            <div className={style.message} key={index}>
              {msg.content}
              {msg.files?.map((file, fileIndex) => (
                <div key={fileIndex} className={style.fileItem}>
                  <p className={style.fileMessage}>{file.name}</p>
                </div>
              ))}
            </div>
          ))}</div>

          <div className={style.reponse}> test</div>
        </Grid>

        {/* ZONE D'INPUT */}
        <div
          className={`${style.newchatInput} ${
            messages.length === 0 ? style.inputCentered : style.inputBottom
          }`}
        >
          {/* UPLOAD UN FICHIER (PDF OU WORD) */}
          <div className={style.uploadSection}>
            <label className={style.uploadButton} htmlFor="upload-file">
              <Image className={style.uploadIcon} src={uploadIcon} alt="i" />{" "}
              PDF
            </label>

            {/* INPUT DE FICHIERS */}
            <input
              id="upload-file"
              type="file"
              className={style.addButton}
              accept=".doc, .docx, .pdf"
              multiple
              onChange={handleFileChange}
            />

            {/* AFFICHAGE DES FICHIERS */}
            <div className={style.fileList}>
              {files.map((file, index) => (
                <div key={index} className={style.fileItem}>
                  <button
                    className={style.deleteButton}
                    onClick={() => removeFile(index)}
                  >
                    X
                  </button>
                  <p>{file.name}</p>
                </div>
              ))}
            </div>
          </div>

          {/* INPUT D'UN MESSAGE AU CHABOT */}
          <ChatInput onSend={handleSendMessage} />
        </div>
        {/* <div className={style.footer}>f</div> */}
      </div>
    </main>
  );
}
