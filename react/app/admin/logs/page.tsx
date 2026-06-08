"use client";

import React from 'react';
import Link from 'next/link';

export default function LogsPage() {
  // On simule les données des logs
  // Plus tard, ces données viendront d'une API ou d'une base de données
  const logEntries = [
    { id: 1, user: "Utilisateur Alpha", status: "Connecté", ip: "192.168.1.1", date: "2026-04-02" },
    { id: 2, user: "Admin", status: "Échec", ip: "172.16.254.1", date: "2026-04-02" },
    { id: 3, user: "Utilisateur Beta", status: "Connecté", ip: "192.168.1.45", date: "2026-04-03" },
    { id: 4, user: "Inconnu", status: "Échec", ip: "45.12.89.10", date: "2026-04-03" },
    { id: 5, user: "Utilisateur Gamma", status: "Déconnecté", ip: "192.168.1.12", date: "2026-04-04" },
  ];

  const handleRefresh = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Actualisation des logs...");
    // Logique pour récupérer les nouveaux logs ici
  };

  return (
    <>
      <p className="app-description">
        Consultez ici l&apos;historique complet des accès et des tentatives de connexion au système.
      </p>

      <div className="log-content">
        <div className="log-data">
          
          <form onSubmit={handleRefresh}>
            <input 
              type="submit" 
              value="Rechercher / Actualiser" 
              className="btn-apply"
              style={{ marginBottom: '20px', width: 'auto', cursor: 'pointer' }}
            />
          </form>

          <div className="table-container">
            <table className="show-data">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Utilisateur</th>
                  <th>État de la connexion</th>
                  <th>Adresse IP</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {logEntries.map((log, index) => (
                  <tr key={log.id}>
                    {/* On peut utiliser log.id ou index + 1 */}
                    <td>{index + 1}</td>
                    <td>
                      <Link href={`/admin/users/${log.id}`} className="log-user">
                        {log.user}
                      </Link>
                    </td>
                    <td style={{ 
                      color: log.status === "Échec" ? "#ff4d4d" : 
                             log.status === "Connecté" ? "#2ecc71" : "inherit",
                      fontWeight: 'bold'
                    }}>
                      {log.status}
                    </td>
                    <td>{log.ip}</td>
                    <td>{log.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
