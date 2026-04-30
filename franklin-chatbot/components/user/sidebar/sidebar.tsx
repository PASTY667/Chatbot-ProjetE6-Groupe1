"use client";
import Image from "next/image";
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
              <Link href="/">Nouveau chat +</Link>
            </li>
          </div>
          <hr className={style.hrSidebar} />
          <div className={style.listChatSidebar}>
            <li>
              <Link href="/">Chat</Link>
            </li>
          </div>
        </ul>
      </div>
      <div className={style.setting}>
        <h5 className={style.settingTitle}>Paramètres</h5>
        <Link className={style.settingButton} href="/settings">
          <Image className={style.logo} src="/next.svg" alt="settings" width={20} height={20} />
          <Image className={style.logoHover} src="/globe.svg" alt="settings-hover" width={20} height={20} />
        </Link>
      </div>
    </div>
  );
}
