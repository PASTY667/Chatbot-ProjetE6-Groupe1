"use client"; 

import React, { useState } from 'react';

export default function StatsPage() {
  const [filters, setFilters] = useState({
    user: 'all',
    startDate: '',
    endDate: '',
    success: true,
    fail: true
  });

  const handleApplyFilters = () => {
    console.log("Filtres appliqués :", filters);
  };

  return (
    <>
      <p className="app-description">
        Consultez ici l'historique complet des accès et des tentatives de connexion au système.
      </p>

      <div className="log-content">
        <div className="stats-container">
          
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
                <option value="1">Utilisateur 1</option>
                <option value="2">Utilisateur 2</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Depuis</label>
              <input 
                type="date" 
                onChange={(e) => setFilters({...filters, startDate: e.target.value})}
              />
            </div>

            {/* <div className="filter-group">
              <label>Type d'accès</label>
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
            </div> */}

            <button className="btn-apply" onClick={handleApplyFilters}>
              Appliquer les filtres
            </button>
          </aside>
          
          <section className="stats-visual">
            <div className="chart-header">
              <h2>Statistiques d'utilisation</h2>
            </div>
            <div className="chart-placeholder">
              <p></p>
            </div>
          </section>

        </div>
      </div>
    </>
  );
}