import React from 'react';
import { prisma } from '@/lib/prisma'
import Link from 'next/link';

export default async function LogsPage() {
  /* const [logEntries, setLogEntries] = useState([
    { id: 1, user: "Utilisateur 1", status: "Connecté", ip: "192.168.1.1", date: "2026-04-02" },
    { id: 2, user: "Admin", status: "Déconnecté", ip: "172.16.254.1", date: "2026-04-02" },
    { id: 3, user: "Utilisateur 2", status: "Connecté", ip: "192.168.1.45", date: "2026-04-03" },
    { id: 4, user: "Inconnu", status: "Déconnecté", ip: "45.12.89.10", date: "2026-04-03" },
    { id: 5, user: "Utilisateur 3", status: "Déconnecté", ip: "192.168.1.12", date: "2026-04-04" },
  ]); */

  const logs = await prisma.log.findMany();

  const handleRefresh = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Actualisation des logs...");
  };

  return (
    <>
      <p className="app-description">
        Consulter ici l'historique complet des accès au système.
      </p>

      <div className="log-content">
        <div className="log-data">

          {/* <form onSubmit={handleRefresh}>
            <input 
              type="submit" 
              value="Rechercher / Actualiser" 
              className="btn-apply"
              style={{ marginBottom: '20px', width: 'auto', cursor: 'pointer' }}
            />
          </form> */}

          <div className="table-container">
            <table className="show-data">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Statut de l'utilisateur</th>
                  <th>État de la connexion</th>
                  <th>Adresse IP</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => {
                  return (
                    <tr key={log.id_log}>
                      <td>{log.id_log}</td>
                      <td>
                        <Link href={`/users/${log.id_log}`} className="log-user">
                          aaa
                        </Link>
                      </td>
                      <td style={{ fontWeight: 'bold' }}>
                        {log.state ? "Connecté" : "Déconnecté"}
                      </td>
                      <td>{log.ip_address}</td>
                      <td>a</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}