import Image from "next/image";
import { TextField, Button, Container, Grid, LinearProgress, CircularProgress } from "@mui/material";

import style from "@/app/index/index.module.css";
import uploadIcon from "@/assets/upload-file.png";
import logo from "@/assets/frankLogo.png";



export default function Index() {
  return (
    <div className={style.newchatPage}>
      {/* HEADER DE LA PAGE */}
      <div className={style.newchatHeader}>
        {/* <Image className={style.logo} src={} alt="" /> */}
        <h1 className={style.newchatTitle}>Franklin</h1>
      </div>

      <Grid container direction="column" spacing={2} paddingBottom={2}>
        {}
      </Grid>


      {/* ZONE D'INPUT */}
      <div className={style.newchatInput}>
        {/* UPLOAD UN FICHIER (PDF OU WORD) */}
        <div className={style.uploadSection}>
          <label htmlFor="upload-file" className={style.uploadButton}>
            <Image className={style.uploadIcon} src={uploadIcon} alt="i" /> PDF
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
        <input
          className={style.textInput}
          type="text"
          // value={message}
          // onChange={(e) => setMessage(e.target.value)}
          placeholder="Poser une question..."
          // value={query}
          // onChange={test}
        />

        {/* BOUTON SOUMETTRE LE MESSAGE */}
        <input className={style.submitButton} type="submit" value=">" />
      </div>
    </div>
  );
}
