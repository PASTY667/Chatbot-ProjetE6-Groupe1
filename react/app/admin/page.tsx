import AppCard from '@/components/admin/AppCard';

const APPS = [
  { title: 'Logs', desc: "Alors qu'est-ce qu'on a là", href: '/admin/logs' },
  { title: 'Gestion des fichiers', desc: 'Organisation des documents', href: '/admin/files' },
  { title: 'Statistiques', desc: 'Analyse des données', href: '/admin/stats' },
  { title: 'Utilisateurs', desc: 'Administration des comptes', href: '/admin/users' },
];

export default function Dashboard() {
  return (
    <section className="apps-grid">
      {APPS.map((app) => (
        <AppCard key={app.href} {...app} />
      ))}
    </section>
  );
}
