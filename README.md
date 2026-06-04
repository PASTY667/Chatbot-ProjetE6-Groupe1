# Chatbot-ProjetE6-Groupe1
Projet etudiant d'un chatbot intranet base sur une technologie RAG.

## Changements apportes

- Recuperation et integration de l'interface web Next.js dans `react/`.
- Remise en place de l'authentification LDAP/NextAuth pour la connexion utilisateur.
- Nettoyage de l'auth locale de test creee pour les essais.
- Ajout de routes proxy Next.js pour :
  - le token backend,
  - l'upload de documents,
  - le chat en mode stream.
- Branchement du chat web sur `POST /chat/query/stream`.
- Branchement de l'upload web sur `POST /ingest/upload`.
- Ajout de la verification health cote frontend sur `/api/health`.
- Ajustement du nombre de contextes recuperes par le chat a `k = 2`.
- Correction de la configuration frontend pour le lancement local sur `http://localhost:3000`.

## Execution locale

Le frontend se lance depuis `react/` avec :

```bash
npm install
npm run dev
```

Le backend Python expose l'API RAG, l'auth et l'ingestion.
