# Franklin (application unifiée)

Cette application Next.js regroupe:
- l'interface utilisateur (chat) sur les routes existantes (`/`, `/settings`)
- l'interface administrateur sous le préfixe `/admin`

## Lancement local

```bash
npm install
npm run dev
```

Puis ouvrir `http://localhost:3000`.

## Routes principales

- User:
  - `/`
  - `/settings`
- Admin:
  - `/admin`
  - `/admin/logs`
  - `/admin/files`
  - `/admin/stats`
  - `/admin/users`

## Compatibilité de routes admin historiques

Les anciennes routes directes sont redirigées vers `/admin/*`:
- `/logs` -> `/admin/logs`
- `/files` -> `/admin/files`
- `/stats` -> `/admin/stats`
- `/users` -> `/admin/users`

## Base de données

Aucune base de données locale n'est requise pour afficher les pages user/admin actuelles de cette application fusionnée.
