"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { signOut } from "next-auth/react";

import logo from "@/assets/settingLogo.png";
import logoHover from "@/assets/settingLogoHover.png";
import type { ChatSession } from "@/app/page";

import style from "./sidebar.module.css";

type SidebarProps = {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onCreateSession: () => void;
  onSelectSession: (sessionId: string) => void;
  onRenameSession: (sessionId: string, title: string) => void;
  authStatus: "authenticated" | "loading" | "unauthenticated";
  displayName: string | null;
  canCreateSession: boolean;
  storageError: string;
};

export default function Sidebar({
  sessions,
  activeSessionId,
  onCreateSession,
  onSelectSession,
  onRenameSession,
  authStatus,
  displayName,
  canCreateSession,
  storageError,
}: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [draftTitle, setDraftTitle] = useState("");

  const handleSignOut = () => {
    localStorage.removeItem("backend_access_token");
    localStorage.removeItem("backend_token_type");
    localStorage.removeItem("backend_token_expires_in");
    localStorage.removeItem("backend_subject");
    localStorage.removeItem("backend_role");
    localStorage.removeItem("backend_groups");

    void signOut({ callbackUrl: "/login" });
  };

  const startRename = (session: ChatSession) => {
    setEditingSessionId(session.id);
    setDraftTitle(session.title);
  };

  const submitRename = () => {
    if (!editingSessionId) return;

    onRenameSession(editingSessionId, draftTitle);
    setEditingSessionId(null);
    setDraftTitle("");
  };

  return (
    <aside className={`${style.sidebar} ${collapsed ? style.collapsed : ""}`}>
      <div className={style.upperContent}>
        <div className={style.headerSidebar}>
          <Link href="/" className={style.titleSidebar}>
            Franklin
          </Link>
          <button
            className={style.buttonSidebar}
            onClick={() => setCollapsed((prev) => !prev)}
            aria-label="Toggle sidebar"
            type="button"
          >
            {collapsed ? ">" : "<"}
          </button>
        </div>

        <div className={style.sessionSection}>
          <button
            className={style.newChatButton}
            onClick={onCreateSession}
            type="button"
            disabled={!canCreateSession}
          >
            Nouveau chat +
          </button>

          <div className={style.authHint}>
            {authStatus === "authenticated"
              ? `Connecte en tant que ${displayName ?? "utilisateur"}`
              : "Navigation visible sans LDAP. La creation de chats, le chat IA et l'upload demandent une connexion LDAP."}
          </div>
          {storageError && <div className={style.storageError}>{storageError}</div>}

          <ul className={style.listSidebar}>
            {sessions.map((session) => (
              <li key={session.id}>
                {editingSessionId === session.id ? (
                  <form
                    className={style.renameForm}
                    onSubmit={(event) => {
                      event.preventDefault();
                      submitRename();
                    }}
                  >
                    <input
                      className={style.renameInput}
                      value={draftTitle}
                      onChange={(event) => setDraftTitle(event.target.value)}
                    />
                    <button className={style.renameSubmit} type="submit">
                      OK
                    </button>
                  </form>
                ) : (
                  <div
                    className={`${style.chatItem} ${session.id === activeSessionId ? style.activeChat : ""}`}
                  >
                    <button
                      className={style.chatLink}
                      onClick={() => onSelectSession(session.id)}
                      type="button"
                    >
                      <span className={style.chatTitle}>{session.title}</span>
                      <span className={style.chatMeta}>
                        {session.messages.length} message{session.messages.length > 1 ? "s" : ""}
                      </span>
                    </button>
                    <button
                      className={style.renameButton}
                      onClick={() => startRename(session)}
                      type="button"
                    >
                      Renommer
                    </button>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className={style.setting}>
        <div className={style.settingText}>
          <h5 className={style.settingTitle}>
            {authStatus === "authenticated" ? "Session active" : "Connexion requise"}
          </h5>
          <p className={style.settingDescription}>
            {authStatus === "authenticated"
              ? displayName ?? "Utilisateur"
              : "Utilisez le login LDAP pour activer les appels IA et la persistance serveur."}
          </p>
        </div>
        <div className={style.settingActions}>
          {authStatus === "authenticated" ? (
            <button className={style.logoutButton} type="button" onClick={handleSignOut}>
              Se deconnecter
            </button>
          ) : (
            <Link className={style.loginButton} href="/login">
              Se connecter
            </Link>
          )}
          <Link className={style.settingButton} href="/settings">
            <Image className={style.logo} src={logo} alt="logo" />
            <Image className={style.logoHover} src={logoHover} alt="logoHover" />
          </Link>
        </div>
      </div>
    </aside>
  );
}
