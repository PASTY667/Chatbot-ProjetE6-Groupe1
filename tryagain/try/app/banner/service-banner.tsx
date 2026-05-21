"use client";
import { useHealth } from "@/app/providers";

export function ServiceBanner() {
  const { health, loading } = useHealth();

  if (loading || !health || health.status_ok) return null;

  return (
    <div style={{ background: "#f59e0b", color: "white", padding: "12px", zIndex:100}}>
      Service dégradé ou indisponible
    </div>
  );
}