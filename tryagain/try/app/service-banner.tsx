"use client";
import { useHealth } from "@/app/providers";
import style from "@/app/service-banner.module.css";

export default function ServiceBanner() {
  const { health, loading } = useHealth();

  if (loading || !health || health.status_ok) return null;

  return (
    <div className={style.banner}>
      Service dégradé ou indisponible
    </div>
  );
}