import React from 'react';

import { prisma } from '@/lib/prisma';

export default async function UsersManagementPage() {
  // Données fictives pour les utilisateurs
  /* const [users, setUsers] = useState([
    { id: 1, name: "sniffsniff", role: "Administrateur", ip: "192.168.1.15", lastLogin: "2026-04-02" },
    { id: 2, name: "Jean Dupont", role: "Utilisateur", ip: "82.12.45.67", lastLogin: "2026-04-06" },
    { id: 3, name: "Marie Curie", role: "Modérateur", ip: "10.0.0.5", lastLogin: "2026-04-07" },
  ]);

  /*const handleBlock = (id: number) => {
    alert(`Utilisateur ${id} bloqué (logique à implémenter)`);
  };

  const handleDelete = (id: number) => {
    if(confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) {
      setUsers(users.filter(user => user.id !== id));
    }
  }; */
  const users = await prisma.user.findMany();

  type UserType = typeof users[number];


  return (
    <>

      <p className="app-description">
        Gérer les comptes utilisateurs et contrôler les accès au système.
      </p>

      <div className="log-content">
        <div className="log-data">

          <div className="table-container">
            <table className="show-data">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Nom de l'utilisateur</th>
                  <th>Rôle</th>
                  <th>Adresse IP</th>
                  <th>Dernière connexion</th>
                  <th>Bloquer / Supprimer</th>
                </tr>
              </thead>
              <tbody>
                
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}