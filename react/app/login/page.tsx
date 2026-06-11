"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import style from "@/app/login/login.module.css";

export default function Login() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setError("");
    setLoading(true);

    try {
      const result = await signIn("credentials", {
        username,
        password,
        redirect: false,
        callbackUrl: "/",
      });

      if (result?.error) {
        setError("Identifiants invalides");
        return;
      }

      try {
        const tokenRes = await fetch("/api/backend-auth/token", {
          method: "POST",
        });
        const data = await tokenRes.json().catch(() => ({}));

        if (tokenRes.ok && data.access_token) {
          localStorage.setItem("backend_access_token", data.access_token);
          localStorage.setItem("backend_token_type", data.token_type ?? "bearer");
          localStorage.setItem("backend_token_expires_in", String(data.expires_in ?? ""));
          localStorage.setItem("backend_subject", data.username ?? username);
          localStorage.setItem("backend_role", data.role ?? "user");
          localStorage.setItem("backend_groups", JSON.stringify(data.groups ?? []));
        } else {
          localStorage.removeItem("backend_access_token");
          localStorage.removeItem("backend_token_type");
          localStorage.removeItem("backend_token_expires_in");
          localStorage.removeItem("backend_subject");
          localStorage.removeItem("backend_role");
          localStorage.removeItem("backend_groups");
          console.warn("Backend token unavailable after LDAP login", data);
        }
      } catch (tokenError) {
        localStorage.removeItem("backend_access_token");
        localStorage.removeItem("backend_token_type");
        localStorage.removeItem("backend_token_expires_in");
        localStorage.removeItem("backend_subject");
        localStorage.removeItem("backend_role");
        localStorage.removeItem("backend_groups");
        console.warn("Backend token request failed after LDAP login", tokenError);
      }

      router.replace(result?.url ?? "/");
    } catch {
      setError("Connexion impossible");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={style.login}>
      <h1 className={style.headline}>Bienvenue!</h1>

      <div className={style.loginSection}>
        <h3 className={style.loginTitle}>Connexion</h3>

        <h5 className={style.loginText}>Nom d&apos;utilisateur</h5>
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
          <button className={style.loginButton} onClick={handleLogin} disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </div>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    </div>
  );
}
