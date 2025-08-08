# Cloud App (Supabase Edge Functions)

This folder contains a minimal scaffold for a Supabase-based backend that supports the SnapshotPlot publisher contract.

## What you get
- SQL migrations for projects/collections/snapshots with basic RLS
- Edge functions:
  - `snapshots-publish`: creates a pending snapshot and returns upload URLs
  - `upload-artifact`: receives PUTs for `code` or `plot` and stores them to Supabase Storage
  - `snapshots-finalize`: marks the snapshot as complete

## Prereqs
- Supabase CLI installed
- A Supabase project (set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` for local testing)

## Quick start
```bash
cd cloud
supabase init  # if not already
supabase db push  # apply migrations

# Run functions locally
supabase functions serve --env-file ./env.local
```

Publish functions:
```bash
supabase functions deploy snapshots-publish
supabase functions deploy upload-artifact
supabase functions deploy snapshots-finalize
```

Environment variables (env.local):
```
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
```

## API
- POST functions/v1/snapshots-publish
- PUT functions/v1/upload-artifact?project_id=...&snapshot_id=...&artifact=code|plot&token=...
- POST functions/v1/snapshots-finalize

These endpoints match the contract in `CLOUD_BACKEND_SPEC.md`. 