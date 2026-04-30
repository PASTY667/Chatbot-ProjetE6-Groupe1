"use client";

import React, { useState } from 'react';
import Link from 'next/link';

export default function FilesPage() {
  // Simulation de données (à remplacer par un fetch plus tard)
  const [files, setFiles] = useState([
    { id: 1, name: "sniffsniff", format: "PDF", user: "Utilisateur Alpha", date: "2026-04-02" },
    { id: 2, name: "budget_2026", format: "XLSX", user: "Admin", date: "2026-04-05" },
    // Ajoute d'autres fichiers ici
  ]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Recherche lancée...");
  };

  return (
    <>

      <p className="app-description">
        Consultez ici l'historique complet des accès et des tentatives de connexion au système.
      </p>

      <div className="log-content">
        <div className="log-data">
          
          <form onSubmit={handleSearch}>
            <input 
              type="submit" 
              value="Rechercher" 
              name="submit" 
              id="refresh" 
              className="btn-apply" // On réutilise ton style de bouton
              style={{ marginBottom: '20px', width: 'auto', cursor: 'pointer' }}
            />
          </form>

          <div className="table-container">
            <table className="show-data">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Nom du fichier</th>
                  <th>Format</th>
                  <th>Ajouté par</th>
                  <th>Date d'ajout</th>
                  <th>Modifier / Supprimer</th>
                </tr>
              </thead>
              <tbody>
                {files.map((file) => (
                  <tr key={file.id}>
                    <td>{file.id}</td>
                    <td>{file.name}</td>
                    <td>{file.format}</td>
                    <td>
                      <Link href={`/users/${file.id}`} className="log-user">
                        {file.user}
                      </Link>
                    </td>
                    <td>{file.date}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
                        <button title="Modifier" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>📝</button>
                        <button title="Supprimer" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>🗑️</button>
                      </div>
                    </td>
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