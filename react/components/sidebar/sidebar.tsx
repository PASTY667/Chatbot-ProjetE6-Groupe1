"use client";
import React, { useState } from "react";
import Image from "next/image";
import logo from "@/assets/settingLogo.png";
import logoHover from "@/assets/settingLogoHover.png";
import style from "./sidebar.module.css";
import Link from "next/link";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`${style.sidebar} ${collapsed ? style.collapsed : ""}`}>
      <div className={style.upperContent}>
        <div className={style.headerSidebar}>
          <Link href="/" className={style.titleSidebar}>
            Franklin
          </Link>
          <button
            className={style.buttonSidebar}
            onClick={() => setCollapsed((prev) => !prev)}
            aria-label="Toggle sidebar"
          >
            {collapsed ? ">" : "<"}
          </button>
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
          <Image className={style.logo} src={logo} alt="logo" />
          <Image className={style.logoHover} src={logoHover} alt="logoHover" />
        </Link>
      </div>
    </div>
  );
}
