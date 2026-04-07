import AppCard from "@/components/AppCard";

const APPS = [
  { title: "Logs", desc: "Alors qu'est-ce qu'on a là", href: "/logs" },
  { title: "Gestion des fichiers", desc: "Organisation des documents", href: "/files" },
  { title: "Statistiques", desc: "Analyse des données", href: "/stats" },
  { title: "Utilisateurs", desc: "Administration des comptes", href: "/users" },
];

export default function Dashboard() {
  return (
    <>
      <header className="page-header">
        <h1 className="page-title">Franklin</h1>
      </header>

      <section className="apps-grid">
        {APPS.map((app) => (
          <AppCard key={app.href} {...app} />
        ))}
      </section>
    </>
  );
}