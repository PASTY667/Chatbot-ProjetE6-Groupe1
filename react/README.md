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

## Prisma / DB

Les dépendances Prisma des deux versions sont prises en compte (`prisma`, `@prisma/client`, `pg`, `dotenv`) ainsi que le schéma `prisma/schema.prisma`.

Les pages user/admin ne dépendent pas d'une DB locale pour s'afficher.
Le helper `lib/prisma.ts` retourne `null` si `DATABASE_URL` n'est pas définie afin de ne pas bloquer le boot local.
