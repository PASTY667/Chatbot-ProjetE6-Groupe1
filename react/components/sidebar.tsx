"use client";
import Image from "next/image";
import logo from "@/assets/settingLogo.png";
import logoHover from "@/assets/settingLogoHover.png";
import style from "./sidebar.module.css";
import Link from "next/link";

export default function Sidebar() {
  return (
    <div className={style.sidebar}>
      <div>
        <div className={style.headerSidebar}>
          <h3 className={style.titleSidebar}>Franklin</h3>
          <button className={style.buttonSidebar}>-</button>
        </div>
        <ul className={style.listSidebar}>
          <div className={style.listFixSidebar}>
            <li>
              <a href="index.tsx">Nouveau chat +</a>
            </li>
            <li>
              <a href="history.tsx">Historique</a>
            </li>
          </div>
          {/* <hr className={style.hrSidebar}> */}
          <div className={style.listChatSidebar}>
            <li>
              <Link href="newchat.tsx">Chat</Link>
            </li>
            <li>
              <Link href="newchat.tsx">Chat</Link>
            </li>
            <li>
              <Link href="newchat.tsx">Chat</Link>
            </li>
          </div>
        </ul>
      </div>
      <div className={style.setting}>
        <h5 className={style.settingTitle}>Paramètres</h5>
        <a className={style.settingButton} href="settings.tsx">
          <Image className={style.logo} src={logo} alt="logo" />
          <Image className={style.logoHover} src={logoHover} alt="logoHover" />
        </a>
      </div>
    </div>
  );
}
