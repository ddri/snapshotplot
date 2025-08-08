# SnapshotPlot Cloud App (Next.js + Supabase)

Minimal Next.js server (API routes) that implements the publisher endpoints from `CLOUD_BACKEND_SPEC.md`.

## Features
- POST `/api/snapshots/publish`: create pending snapshot and return upload URLs
- PUT `/api/snapshots/upload-artifact`: accept code/plot uploads and store to Supabase Storage
- POST `/api/snapshots/finalize`: mark snapshot complete

## Setup
```bash
cd cloud/app
cp .env.example .env.local  # fill in SUPABASE_URL and SUPABASE_SERVICE_ROLE
npm install
npm run dev
```

Env vars (`.env.local`):
```
SUPABASE_URL=...       # Supabase project API URL
SUPABASE_SERVICE_ROLE=...  # service role key (server-only)
BASE_URL=http://localhost:3000  # public base URL for building upload URLs
BUCKET_CODE=code
BUCKET_PLOTS=plots
```

## Notes
- These API routes use the Supabase service role key on the server; do not expose to client.
- For production, host this app (e.g., Vercel) and configure environment variables. 