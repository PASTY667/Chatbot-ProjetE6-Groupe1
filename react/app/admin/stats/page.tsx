"use client"; // Obligatoire car on va utiliser des interactions (boutons, inputs)

import React, { useState } from 'react';

export default function StatsPage() {
  // Exemple d'état pour les filtres
  const [filters, setFilters] = useState({
    user: 'all',
    startDate: '',
    endDate: '',
    success: true,
    fail: true
  });

  const handleApplyFilters = () => {
    console.log("Filtres appliqués :", filters);
    // Ici tu feras ton appel API plus tard
  };

  return (
    <>
      <p className="app-description">
        Consultez ici l&apos;historique complet des accès et des tentatives de connexion au système.
      </p>

      <div className="log-content">
        <div className="stats-container">
          
          {/* ASIDE - FILTRES */}
          <aside className="stats-filters">
            <h3>Filtres</h3>

            <div className="filter-group">
              <label htmlFor="user-select">Sélectionner Utilisateur</label>
              <select 
                id="user-select" 
                value={filters.user}
                onChange={(e) => setFilters({...filters, user: e.target.value})}
              >
                <option value="all">Tous les utilisateurs</option>
                <option value="1">Utilisateur Alpha</option>
                <option value="2">Utilisateur Beta</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Période</label>
              <input 
                type="date" 
                onChange={(e) => setFilters({...filters, startDate: e.target.value})}
              />
              <input 
                type="date" 
                onChange={(e) => setFilters({...filters, endDate: e.target.value})}
              />
            </div>

            <div className="filter-group">
              <label>Type d&apos;accès</label>
              <div className="checkbox-item">
                <input 
                  type="checkbox" 
                  id="success" 
                  checked={filters.success}
                  onChange={(e) => setFilters({...filters, success: e.target.checked})}
                /> 
                <label htmlFor="success">Réussis</label>
              </div>
              <div className="checkbox-item">
                <input 
                  type="checkbox" 
                  id="fail" 
                  checked={filters.fail}
                  onChange={(e) => setFilters({...filters, fail: e.target.checked})}
                /> 
                <label htmlFor="fail">Échecs</label>
              </div>
            </div>

            <button className="btn-apply" onClick={handleApplyFilters}>
              Appliquer les filtres
            </button>
          </aside>

          {/* SECTION - VISUALISATION */}
          <section className="stats-visual">
            <div className="chart-header">
              <h2>Statistiques d&apos;utilisation</h2>
            </div>
            <div className="chart-placeholder">
              <p>Emplacement du graphique (Stats Utilisateurs)</p>
            </div>
          </section>

        </div>
      </div>
    </>
  );
}
