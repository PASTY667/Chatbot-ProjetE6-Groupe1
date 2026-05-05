"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import style from "@/app/login/login.module.css";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");

  async function handleLogin() {
    setError("");

    const res = await signIn("credentials", {
      username,
      password,
      redirect: true,
      callbackUrl: "/",
    });

    if (res?.error) {
      setError("Identifiants invalides");
    }
  }

  return (
    <div className={style.login}>
      <h1 className={style.headline}>Bienvenue!</h1>

      <div className={style.loginSection}>
        <h3 className={style.loginTitle}>Connexion</h3>

        <h5 className={style.loginText}>Nom d'utilisateur</h5>
        <input
          className={style.inputUser}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <h5 className={style.loginText}>Mot de passe</h5>
        <input
          className={style.inputPwd}
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => {
          if (e.key === "Enter") handleLogin();
        }}
        />
        <div className={style.divButton}>
          <button className={style.loginButton} onClick={handleLogin}>
            Se connecter
          </button>
        </div>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    </div>
  );
}
