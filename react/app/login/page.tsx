"use client";

import { useState } from "react";
import { signIn, getSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import style from "@/app/login/login.module.css";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const router = useRouter();

  async function handleLogin() {
    console.log("LOGIN CLICKED");
    setError("");

    const res = await signIn("credentials", {
      username,
      password,
      redirect: false,
    });

    console.log("SIGNIN RESULT:", res);

    if (res?.error) {
      setError("Identifiants invalides");
      return;
    }

    const session = await getSession();

    const role = session?.user?.role;

    if (role === "admin") {
      router.push("/admin");
      return;
    }

    if (role === "user") {
      router.push("/user");
      return;
    }

    router.push("/");
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
