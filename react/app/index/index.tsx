import Image from "next/image";
import style from "@/app/index/index.module.css";
import uploadIcon from "@/assets/upload-file.png";
import logo from "@/assets/frankLogo.png";

export default function Index() {
  return (
    <div className={style.newchatPage}>
      <div className={style.newchatHeader}>
        {/* <Image className={style.logo} src={} alt="" /> */}
      <h1 className={style.newchatTitle}>Franklin</h1>
    </div>
    <div className={style.newchatInput}>
      <div className={style.uploadSection}>
        <label htmlFor="upload-file" className={style.uploadButton}>
          <Image className={style.uploadIcon} src={uploadIcon} alt="i" /> PDF
        </label>
        <span id="file-name" className={style.fileName}></span>
        <input id="upload-file" type="file" className={style.addButton} accept="application/pdf" />
      </div>
      {/* <input className={style.textInput} type="text" value="Poser une question..." /> */}
      <input className={style.submitButton} type="submit" value=">" />
      </div>
    </div>
  );
}
