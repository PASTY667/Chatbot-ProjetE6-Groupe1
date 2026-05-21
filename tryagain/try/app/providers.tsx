"use client";
import { SessionProvider } from "next-auth/react";
import { useEffect, useState, createContext, useContext } from "react";

type HealthStatus = {
  status_ok: boolean;
  chroma_ok: boolean;
  ollama_ok: boolean;
  jwt_secret_ok: boolean;
};

type HealthContextType = {
  health: HealthStatus | null;
  loading: boolean;
};

const HealthContext = createContext<HealthContextType>({
  health: null,
  loading: true,
});

function HealthProvider({ children }: { children: React.ReactNode }) {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/health", { cache: "no-store" })
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() =>
        setHealth({
          status_ok: false,
          chroma_ok: false,
          ollama_ok: false,
          jwt_secret_ok: false,
        }),
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <HealthContext.Provider value={{ health, loading }}>
      {children}
    </HealthContext.Provider>
  );
}

export function useHealth() {
  return useContext(HealthContext);
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <HealthProvider>{children}</HealthProvider>
    </SessionProvider>
  );
}
